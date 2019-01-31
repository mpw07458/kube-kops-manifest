#!/usr/bin/env bash
## Setup vars
source vault.env
# Please note that this filename of cni asset may change with kubernetes version
export CNI_FILENAME=cni-amd64-0799f5732f2a11b329d9e3d51b9c8f2e3759f2ff.tar.gz

export KOPS_BASE_URL=https://s3-website-us-gov-west-1.amazonaws.com/$ASSET_BUCKET/kops/$KOPS_VERSION/
export CNI_VERSION_URL=https://s3-website-us-gov-west-1.amazonaws.com/$ASSET_BUCKET/kubernetes/network-plugins/$CNI_FILENAME
cd wheel
dzdo python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index virtualenv-16.1.0-py2.py3-none-any.whl
cd ..
dzdo virtualenv venv
dzdo chown $USER:$USER -R venv
cp -p wheel/* venv/bin/.
cd venv/bin
tar xvf PyYAML-3.13.tar.gz
cd PyYAML-3.13
../python3.6 setup.py install
cd ..
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index MarkupSafe-1.1.0-cp36-cp36m-manylinux1_x86_64.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index Jinja2-2.10-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index pip-18.1-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index setuptools-40.6.2-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index urllib3-1.24.1-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index certifi-2018.10.15-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index chardet-3.0.4-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index idna-2.7-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index h11-0.8.1-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index requests-2.20.1-py2.py3-none-any.whl
./python3.6 pip-18.1-py2.py3-none-any.whl/pip install --no-index hvac-0.7.0-py2.py3-none-any.whl
cd ../..
export PYTHONUSERBASE=$HOME
export CURRENTDIR=`pwd`
source $CURRENTDIR/venv/bin/activate
source vault.env
