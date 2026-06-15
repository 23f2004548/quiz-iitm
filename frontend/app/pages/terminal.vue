<template>
  <div class="h-[calc(100vh-3.5rem)] p-6 flex flex-col">
    <div class="mb-4 flex-shrink-0 select-none">
      <h1 class="text-3xl font-bold tracking-tight text-ink mb-1">Interactive Sandbox</h1>
      <p class="text-ink-muted text-sm">Experiment with multiple configurations (Ubuntu, GitBash, Jupyter, Python, SQL, JS, HTML/CSS, Java, C++, Rust) in a safe, sandboxed workspace.</p>
    </div>
    
    <div class="flex-1 min-h-0 bg-surface rounded-xl border border-hairline overflow-hidden shadow-notion-soft p-1">
      <Sandbox />
    </div>
  </div>
</template>
