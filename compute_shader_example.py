# This code contains an very simple example for how to use compute shaders

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np

# Define the compute shader code
compute_shader_code = """
#version 430 core

layout(local_size_x = 1) in;

layout(std430, binding = 0) buffer DataBuffer {
    int data[];
};

void main() {
    uint index = gl_GlobalInvocationID.x;

    // Increment the data by 2
    data[index] += 2;
}
"""

# Initialize Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Create a buffer object to store the data
data = np.arange(10, dtype=np.int32)
data_buffer = glGenBuffers(1)
glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, data_buffer)
glBufferData(GL_SHADER_STORAGE_BUFFER, data.nbytes, data, GL_DYNAMIC_COPY)

# Create a compute shader program
compute_shader_program = shaders.compileShader(compute_shader_code, GL_COMPUTE_SHADER)
shader_program = shaders.compileProgram(compute_shader_program)

# Get the index of the buffer block in the shader
block_index = glGetProgramResourceIndex(shader_program, GL_SHADER_STORAGE_BLOCK, "DataBuffer")
glShaderStorageBlockBinding(shader_program, block_index, 0)

# Calculate the number of invocations based on the data size
num_invocations = len(data)

# Set up the main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Run the compute shader
    glUseProgram(shader_program)
    glDispatchCompute(num_invocations, 1, 1)
    glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
    glUseProgram(0)

    # Retrieve the updated data from the buffer object
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, data_buffer)
    updated_data = np.frombuffer(glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, data.nbytes), dtype=np.uint32)
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)

    print("Updated Data:", updated_data)

    pygame.display.flip()

pygame.quit()
