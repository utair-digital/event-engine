import setuptools

with open("README.md", "r", encoding='utf-8') as readme:
    long_description = readme.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="event_engine_async",
    version="1.0.0",
    author="utair",
    description="Asynchronous Event engine with kafka bus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.utair.ru/digital/repository/event-engine-async",
    install_requires=required,
    keywords='utair',
    license="Private",
    packages=setuptools.find_packages(exclude=('examples', 'kafka_docker', )),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
