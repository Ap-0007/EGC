const projectPath = req.body.project_path;
const resolvedPath = path.resolve('~/.egc/state/', projectPath);
if (!resolvedPath.startsWith(path.resolve('~/.egc/state/'))) {
  throw new Error('Project path is outside of the intended state directory');
}
const statePath = resolvedPath + '.md';