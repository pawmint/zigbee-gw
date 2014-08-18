# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


readme = open('README.md').read()

setup(
    name='Zigbee-gw',
    version='0.1',
    description='A gateway to use the sensors that communicate through zigbee',
    long_description=readme,
    author='Clément Pallière',
    author_email='clement.palliere@hotmail.fr',
    url='https://github.com/pawmint/zigbee-gw',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ubigate>=0.0.2',
        'pyserial>=2.7',
        'Xbee>=2.0.0'
    ],
    dependency_links=[
        "git+ssh://git@github.com/RomainEndelin/ubiGATE.git@0.0.2#egg=ubiGATE-0.0.2"
    ],
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
