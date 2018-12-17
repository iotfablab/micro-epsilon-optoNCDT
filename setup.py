from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='deflection',
      version='1.2',
      description='Extract Micro-Epsilon OptoNCDT values and store into InfluxDB',
      long_description=readme(),
      url='https://github.com/iotfablab/micro-epsilon-OptoNCDT',
      author='Shantanoo Desai',
      author_email='des@biba.uni-bremen.de',
      license='MIT',
      packages=['deflection'],
      scripts=['bin/deflection'],
      install_requires=[
            'influxdb'
      ],
      include_data_package=True,
      zip_safe=False)
