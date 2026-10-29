// ESLint 基础规则：代码写法的机械部分（rules/code-style.md）。只导出纯规则，不引插件：插件会从本仓库目录解析，而这里没有 node_modules
export default {
  "no-console": "error",
  "no-nested-ternary": "error",
  // 项目当前代码超出时，在自己的配置里用当前最复杂函数的值覆盖，写明递减计划，只降不升
  complexity: ["error", 15],
};
