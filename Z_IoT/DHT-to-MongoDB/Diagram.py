#pip install diagram

from diagrams import Diagram, Cluster
from diagrams.custom import Custom
from diagrams.onprem.database import MongoDB
from diagrams.onprem.analytics import Metabase
from diagrams.generic.storage import Storage
from urllib.request import urlretrieve

# Define the URL for the Python icon and the local file name
python_url = "https://github.com/abranhe/languages.abranhe.com/raw/master/languages/python.png"
python_icon = "python.png"

# Download the Python icon from the URL
urlretrieve(python_url, python_icon)

# Specify the desired output filename
output_filename = "./your_workflow_diagram"

with Diagram("Python to MongoDB to Metabase Workflow", show=False, filename=output_filename):
    custom_icon = Custom("Custom", "./DHT11.png")
    python_code = Custom("Python Code", "./python.png")
    mongodb = MongoDB("MongoDB")
    metabase = Metabase("Metabase")

    custom_icon >> python_code >> mongodb >> metabase
