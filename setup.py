from setuptools import setup, find_packages

setup(
    name='log_notify',
    version='0.0.1',
    description='notify your logger info',
    author='shawn wang',
    packages=find_packages('.', include=['log_notify', 'log_notify.*']),
    install_requires=[
        'requests >= 2.10.0',
        'pytz >= 2016.10'
    ],
    zip_safe=True,
)
