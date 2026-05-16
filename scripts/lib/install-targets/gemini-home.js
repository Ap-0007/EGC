const path = require('path');

const {
  createInstallTargetAdapter,
  createRemappedOperation,
  isForeignPlatformPath,
  normalizeRelativePath,
} = require('./helpers');

const GEMINI_EGC_NAMESPACE = 'egc';

function getGeminiManagedDestinationPath(adapter, sourceRelativePath, input) {
  const normalizedSourcePath = normalizeRelativePath(sourceRelativePath);
  const targetRoot = adapter.resolveRoot(input);

  if (normalizedSourcePath === 'rules') {
    return path.join(targetRoot, 'rules', GEMINI_EGC_NAMESPACE);
  }

  if (normalizedSourcePath.startsWith('rules/')) {
    return path.join(
      targetRoot,
      'rules',
      GEMINI_EGC_NAMESPACE,
      normalizedSourcePath.slice('rules/'.length)
    );
  }

  if (normalizedSourcePath === 'skills') {
    return path.join(targetRoot, 'skills', GEMINI_EGC_NAMESPACE);
  }

  if (normalizedSourcePath.startsWith('skills/')) {
    return path.join(
      targetRoot,
      'skills',
      GEMINI_EGC_NAMESPACE,
      normalizedSourcePath.slice('skills/'.length)
    );
  }

  return null;
}

module.exports = createInstallTargetAdapter({
  id: 'egc-home',
  target: 'egc',
  kind: 'home',
  rootSegments: ['.gemini'],
  installStatePathSegments: ['egc', 'install-state.json'],
  nativeRootRelativePath: '.gemini-plugin',
  planOperations(input, adapter) {
    const modules = Array.isArray(input.modules)
      ? input.modules
      : (input.module ? [input.module] : []);
    const planningInput = {
      repoRoot: input.repoRoot,
      projectRoot: input.projectRoot,
      homeDir: input.homeDir,
    };

    return modules.flatMap(module => {
      const paths = Array.isArray(module.paths) ? module.paths : [];
      return paths
        .filter(p => !isForeignPlatformPath(p, adapter.target))
        .map(sourceRelativePath => {
          const managedDestinationPath = getGeminiManagedDestinationPath(
            adapter,
            sourceRelativePath,
            planningInput
          );

          if (managedDestinationPath) {
            return createRemappedOperation(
              adapter,
              module.id,
              sourceRelativePath,
              managedDestinationPath,
              { strategy: 'preserve-relative-path' }
            );
          }

          return adapter.createScaffoldOperation(module.id, sourceRelativePath, planningInput);
        });
    });
  },
});
