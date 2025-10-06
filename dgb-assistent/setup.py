from setuptools import setup, find_packages

setup(
    name='my-python-app',
    version='0.1.0',
    description='A Python application with a GUI that can be installed on any computer.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # List your dependencies here, e.g.:
        # 'tkinter', 'requests',
    ],
    entry_points={
        'console_scripts': [
            'my-python-app=main:main',  # Adjust according to your main function location
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)