# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


readme = open('README.md').read()

setup(
    name='Zigbee-gw',
    version='0.2-beta',
    description='A gateway to use the sensors that communicate through zigbee',
    long_description=readme,
    author='Clément Pallière',
    author_email='clement.palliere@hotmail.fr',
    url='https://github.com/pawmint/zigbee-gw',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ubigate>=0.0.4-alpha',
        'pyserial>=2.7',
        'Xbee>=2.0.0'
    ],
    dependency_links=[
        "git+ssh://git@github.com/RomainEndelin/ubiGATE.git@v0.0.4-alpha#egg=UbiGate-0.0.4-alpha"
    ],
    entry_points = {
        'console_scripts': ['zigbee-gw=zigbee.gateway:main'],
    },
    license='Copyright',
    zip_safe=True,  # To be verified
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Environment :: Console',
        'License :: Other/Proprietary License',
        'Topic :: Scientific/Engineering',
    ],
)
