cmake_minimum_required(VERSION 3.8)
project(plm_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BackendInfo.msg"
  "msg/PartSelected.msg"
  "msg/PartSummary.msg"
  "msg/PlanDescription.msg"
  "msg/SyncResult.msg"
  "srv/DescribePlans.srv"
  "srv/EnsurePlan.srv"
  "srv/ListBackends.srv"
  "srv/ListParts.srv"
  "srv/RecordPlan.srv"
  "srv/SelectPart.srv"
  "srv/SyncNow.srv"
  "srv/UploadPlan.srv"
  "srv/UploadResults.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
