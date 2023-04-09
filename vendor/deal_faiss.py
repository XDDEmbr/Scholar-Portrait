import sys
import tarfile

# Extract faiss_package.tar.gz to vendor/faiss_package directory
with tarfile.open("vendor/faiss_package.tar.gz", "r:gz") as tar:
    tar.extractall("vendor/")

# Add vendor/faiss_package directory to Python path
sys.path.append("vendor/faiss_package")
