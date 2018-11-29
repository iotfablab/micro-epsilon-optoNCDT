from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='deflection',
      version='1.0',
      description='Extract Micro-Epsilon OptoNCDT values and store into InfluxDB',
      long_description=readme(),
      url='https://gitlab.ips.biba.uni-bremen.de/micro-epsilon-optoNCDT',
      author='Shantanoo Desai',
      author_email='des@biba.uni-bremen.de',
      license='GPLv3',
      packages=['deflection'],
      scripts=['bin/deflection'],
      install_requires=[
            'influxdb'
      ],
      include_data_package=True,
      zip_safe=False)
