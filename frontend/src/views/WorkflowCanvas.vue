<template>
  <div ref="canvas" class="w-full h-[600px] border rounded"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as joint from 'jointjs'

const canvas = ref(null)

onMounted(() => {
  const graph = new joint.dia.Graph()
  const paper = new joint.dia.Paper({
    el: canvas.value,
    model: graph,
    width: 1000,
    height: 600,
    gridSize: 10,
    drawGrid: true,
  })

  // Example node
  const rect = new joint.shapes.standard.Rectangle()
  rect.position(100, 30)
  rect.resize(100, 40)
  rect.attr({
    body: { fill: 'lightgreen' },
    label: { text: 'Start', fill: 'black' },
  })
  rect.addTo(graph)
})
</script>
