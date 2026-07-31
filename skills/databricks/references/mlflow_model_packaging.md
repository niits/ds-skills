# MLflow Model Packaging

## Packaging Contract

A model must load and predict in a fresh process without notebook globals. Package:

- Preprocessing and estimator together.
- `input_example` and inferred/explicit signature.
- Exact `pip_requirements` or environment.
- Params, metrics, code/model versions, and relevant metadata.
- Lookup tables, thresholds, embeddings, and other files as model artifacts.

## sklearn Pipeline

```python
import mlflow
from mlflow.models import infer_signature

input_example = X_train.head(5)
signature = infer_signature(X_train, pipeline.predict_proba(X_train)[:, 1])

with mlflow.start_run() as run:
    mlflow.sklearn.log_model(
        sk_model=pipeline,  # fitted preprocessing + estimator
        artifact_path="model",
        input_example=input_example,
        signature=signature,
        pip_requirements=[
            f"scikit-learn=={sklearn.__version__}",
            f"lightgbm=={lightgbm.__version__}",
        ],
    )
    model_uri = f"runs:/{run.info.run_id}/model"
```

## Custom pyfunc and Artifacts

Subclass `mlflow.pyfunc.PythonModel` when prediction needs custom logic or multiple
objects. Pass files through `artifacts` and load them from `context.artifacts` inside
`load_context`; never read a training-notebook path at prediction time.

```python
class ScorerModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.model = joblib.load(context.artifacts["model_file"])

    def predict(self, context, model_input):
        return self.model.predict_proba(model_input)[:, 1]

mlflow.pyfunc.log_model(
    artifact_path="model",
    python_model=ScorerModel(),
    artifacts={"model_file": "/dbfs/tmp/model.joblib"},
    input_example=input_example,
    pip_requirements=["scikit-learn==1.4.2", "joblib==1.4.0"],
)
```

## Unity Catalog Registry

Use three-level model names and aliases. UC does not use model stages.

```python
from mlflow import MlflowClient

mlflow.set_registry_uri("databricks-uc")
result = mlflow.register_model(model_uri, "main.credit.default_scorer")
MlflowClient().set_registered_model_alias(
    "main.credit.default_scorer", "champion", result.version
)
model = mlflow.pyfunc.load_model("models:/main.credit.default_scorer@champion")
```

Legacy workspace stages are deprecated in modern MLflow; use aliases for new UC work.

## Batch Inference

Run scoring as a scheduled idempotent Job with a deterministic input window. Use
`mlflow.pyfunc.spark_udf` for distributed inference and overwrite/merge only the target
partition or keys.

```python
predict_udf = mlflow.pyfunc.spark_udf(
    spark,
    model_uri="models:/main.credit.default_scorer@champion",
    result_type="double",
)
scored = scoring_df.withColumn("score", predict_udf(*scoring_df.columns))
```

## Release Checklist

- Exact dependencies are pinned with `==`.
- Signature and input example enforce schema.
- Preprocessing is inside the artifact.
- External files are logged as artifacts.
- No `spark`, `dbutils`, widgets, globals, or notebook-relative imports are required.
- A cold-process load/predict test passes.
- Consumers load a registry alias rather than a run URI.
- Batch scoring is scheduled, fixed-window, and idempotent.
