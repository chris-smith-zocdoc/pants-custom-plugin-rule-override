
const hasInjectedEnvVar = process.env.INJECTED_ENV_VAR !== undefined;
console.log(`Hello, world!. Injected env var: ${!!hasInjectedEnvVar}`);
