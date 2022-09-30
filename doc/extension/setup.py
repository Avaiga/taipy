from setuptools import find_packages, setup

setup(
    author="Your Company Name",
    author_email="dev@company.com",
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        # "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # license="Apache License 2.0",
    install_requires=["taipy-gui>=2.0"],
    include_package_data=True,
    name="my-custom-lib",
    description="My custom taipy-gui extension template",
    long_description="This package contains a template to easily get started with creating extension libraries for the Taipy GUI.",
    keywords="taipy",
    packages=find_packages(include=["my_custom_lib", "my_custom_lib.*"]),
    version="1.0.0",
    zip_safe=False,
)
