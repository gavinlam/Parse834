Please parse the attached 834 file using python. Persist data into MongoDB using pymongo. A single collection is fine. Your “unit” of work is the contract. Write some example queries in python using pymongo to extract and display data.

- PyCharm IDE -  http://www.jetbrains.com/pycharm/download/index.html - Community Version
- Use HomeBrew to install mongodb - http://brew.sh/
- Create a project directory and a virtual environment within that project
cd pd-code
# installs virtualenv tool to system python installation
sudo easy_install pip virtualenv
# creates virtual environment directory on
virtualenv --use-distribute --no-site-packages venv
# turns on the virtual env
source venv/bin/activate
# caches libraries so you don’t have to download them again 
export PIP_DOWNLOAD_CACHE=venv/pip_cache

pip install pymongo



Virtual Environment Docs - http://www.virtualenv.org/en/latest/
Python Package Index - https://pypi.python.org/pypi

Extra credit do some unit tests with nosetests and rednose




More helpful links

http://docs.python.org/release/2.7/ - we’re using 2.7.5/6

MongoDB
http://docs.mongodb.org/manual/

PyMongo
http://api.mongodb.org/python/current/