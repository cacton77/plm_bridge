from setuptools import find_packages, setup

package_name = 'cad_loader'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools', 'numpy', 'open3d'],
    extras_require={
        # OpenCascade bindings for STEP; meshes load without them.
        'step': ['cadquery-ocp'],
        'test': ['pytest', 'cadquery-ocp'],
    },
    python_requires='>=3.10',
    zip_safe=True,
    maintainer='Colin Acton',
    maintainer_email='actonc@uw.edu',
    description='STEP and mesh loading with B-rep topology for inspection planning.',
    license='TODO',
)
