# Kubernetes Deployment

This tool runs easiest as a Kubernetes deployment in, e.g., k3s.

To deploy this tool:

1. Create a database and table using your database's tools.  A script to create the necessary tables is provided in [schema.sql](schema.sql).  Remember to grant access to the database user that this tool will use.

2. Obtain an API Key from the AESO:  https://api.aeso.ca/web/api/register

3. Obtain an SQLAlchemy-compatible database URL, e.g. `postgresql+psycopg2://user:password@postgresql.host.domain:5432/databasename`, for your target database.

4. Modify the [aesopoll-secret.yaml](aesopoll-secret.yaml) to include Base64-encoded versions of your API key and DB URL.

5. Deploy the Kubernetes manifests:  `kubectl apply -f aesopoll-config.yaml -f aesopoll-secret.yaml -f aesopoll-deployment.yaml`

6. Enjoy your AESO data!

NB:  To Base64-encode your secrets, use something like `echo -n your_secret_value | base64`