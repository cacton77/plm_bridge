from setuptools import find_packages, setup

package_name = 'plm_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test', 'test.*']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
    ],
    # The picker's assets are served by Flask from inside the installed package.
    package_data={'plm_bridge.picker': ['templates/*.html', 'static/*']},
    # The core itself is standard library only; each feature brings its own.
    install_requires=['setuptools'],
    extras_require={
        'dx3': ['requests'],
        'events': ['stomp.py'],
        'picker': ['flask'],
        'thumbnails': ['numpy', 'matplotlib', 'cad_loader'],
        'test': ['pytest', 'requests', 'flask'],
    },
    python_requires='>=3.10',
    zip_safe=False,
    maintainer='Colin Acton',
    maintainer_email='actonc@uw.edu',
    description='Local parts catalog over PLM systems, with plan and result upload.',
    license='TODO',
    entry_points={
        'console_scripts': [
            'plm-bridge = plm_bridge.cli:main',
        ],
    },
)
