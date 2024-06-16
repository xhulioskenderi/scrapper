import os
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from datetime import timedelta
from couchbase.exceptions import AuthenticationException
# needed for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import ClusterOptions, ClusterTimeoutOptions, QueryOptions
from dotenv import load_dotenv



class CouchbaseConnectionManager:
    def __init__(self) -> None:
        load_dotenv()
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.db_port = os.getenv("DB_PORT")
        self.db_host = os.getenv("DB_HOST")

    def get_connection(self) -> Cluster:
        """
        Return a connection to a couchbase cluster
        """
        try:
            auth = PasswordAuthenticator(
                username=self.username,
                password=self.password,
            )
            connection_string = "couchbase://" + self.db_host
            cluster = Cluster(connection_string, ClusterOptions(auth))

            # Wait until the cluster is ready for use.
            cluster.wait_until_ready(timedelta(seconds=5))
            print (cluster)
            return cluster
        except AuthenticationException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}