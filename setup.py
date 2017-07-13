from distutils.core import setup

setup(
    name='pnapi',
    version='0.0.1',
    packages=['pnapi'],
    description='Python panoptes client',
    install_requires=[
        "beautifulsoup4==4.6.0",
        "numpy==1.13.1",
        "requests==2.18.1"
    ],
)
