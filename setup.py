import setuptools
import io
from os import path

# Version
version = "unknown"
with open("finsec/version.py") as f:
    line = f.read().strip()
    version = line.replace("version = ", "").replace('"', '')

# Long Description (i.e. README file)
here = path.abspath(path.dirname(__file__))
with io.open(path.join(here, 'README.MD'), encoding='utf-8') as f:
    long_description = f.read()

# Setup
setuptools.setup(
    name='finsec',
    version=version,
    description='Download historical filing data directly from the United States Securities Exchange Commission (SEC)!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # url='https://github.com/git-shogg/yfinance',
    author='Stephen Hogg',
    author_email='stephen.hogg.sh@gmail.com',
    license='Apache',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 3.10',
    ],
    platforms=['any'],
    keywords='pandas, sec, securities exchange commission, finance, pandas datareader',
    # packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=['beautifulsoup4==4.11.1', 
                        'pandas==1.3.5', 
                        'requests==2.27.1'],
    packages=["finsec"]
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)