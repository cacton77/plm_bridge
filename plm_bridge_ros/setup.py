import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'plm_bridge_ros'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Colin Acton',
    maintainer_email='actonc@uw.edu',
    description='ROS 2 node and launch file for plm_bridge.',
    license='BSD-3-Clause',
    entry_points={
        'console_scripts': [
            'plm_bridge_node = plm_bridge_ros.node:main',
        ],
    },
)
