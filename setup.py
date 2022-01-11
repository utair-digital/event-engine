import setuptools

with open("README.md", "r", encoding='utf-8') as readme:
    long_description = readme.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="event_engine",
    version="1.0.a",
    author="Utair Digital Group",
    description="Asynchronous Event engine with kafka bus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/utair-digital/event-engine",
    install_requires=required,
    keywords='utair',
    license="Apache License 2.0",
    packages=setuptools.find_packages(exclude=('examples', 'kafka_docker', )),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
