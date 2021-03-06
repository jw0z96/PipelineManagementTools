# PipelineManagementTools
Pipeline management tools primarily for use in Autodesk Maya

This project aims to:
  - Provide artists with a simple method for releasing assets.
  - Provide (layout) artists with a simple method for gathering assets.
  - Manage versions of an asset, with descriptions of the changes.
  - Update references to an asset automatically whenever the asset is updated.
  - Provide a method of 'flattening' asset paths into a single project directory to allow easier project transfer to external rendering services.

Requirements:
  - Maya 2017 (2017 is hard coded into some paths)
  - Definition of MAYA_ASSET_DIR as an environment variable (either in Maya.env or ~/.bashrc for now)

Install:
  - Define MAYA_ASSET_DIR as an environment variable pointing to the '3_prod' folder
  - run `sh install.sh`
