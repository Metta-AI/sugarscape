#ifndef _FUNCTIONS_H_
#define _FUNCTIONS_H_

#include "header.h"
#include "libabl_flamegpu.h"

static const __device__ double PI = 3.14159;
static const __device__ int AGENT_STATE_UNOCCUPIED = 0;
static const __device__ int AGENT_STATE_OCCUPIED = 1;
static const __device__ int AGENT_STATE_MOVEMENT_REQUESTED = 2;
static const __device__ int AGENT_STATE_MOVEMENT_UNRESOLVED = 3;
static const __device__ int SUGAR_GROWBACK_RATE = 1;
static const __device__ int min_start_sugar_level = 1;
static const __device__ int max_start_sugar_level = 10;
static const __device__ double radius = 1.5;
static const __device__ int num_timesteps = 100;
static const __device__ double occupiedFrac = 0.1;
static const __device__ int num_agents = 64000;
static const __device__ int grid_width = 252;


static const __device__ int global_max_env_sugar_level = 50;
static const __device__ double sugar_variance = 1587.6;

__FLAME_GPU_INIT_FUNC__ void openabl_init() {
}

__FLAME_GPU_EXIT_FUNC__ void openabl_exit() {
}
__device__ glm::dvec2 random(RNG_rand48 *rand48, glm::dvec2 min, glm::dvec2 max) {
    return glm::dvec2(random(rand48, min.x, max.x), random(rand48, min.y, max.y));
}
__device__ glm::dvec3 random(RNG_rand48 *rand48, glm::dvec3 min, glm::dvec3 max) {
    return glm::dvec3(random(rand48, min.x, max.x), random(rand48, min.y, max.y), random(rand48, min.z, max.z));
}
__device__ double random(RNG_rand48 *rand48, double max) {
    return random(rand48, 0, max);
}
__device__ glm::dvec2 random(RNG_rand48 *rand48, glm::dvec2 max) {
    return random(rand48, glm::dvec2(0), max);
}
__device__ glm::dvec3 random(RNG_rand48 *rand48, glm::dvec3 max) {
    return random(rand48, glm::dvec3(0), max);
}
__device__ int randomInt(RNG_rand48 *rand48, int max) {
    return randomInt(rand48, 0, max);
}
__device__ double clamp(double pos, double min, double max) {
    return ((pos < min) ? min : ((pos > max) ? max : pos));
}
__device__ glm::dvec2 clamp(glm::dvec2 pos, glm::dvec2 min, glm::dvec2 max) {
    return glm::dvec2(((pos.x < min.x) ? min.x : ((pos.x > max.x) ? max.x : pos.x)), ((pos.y < min.y) ? min.y : ((pos.y > max.y) ? max.y : pos.y)));
}
__device__ glm::dvec3 clamp(glm::dvec3 pos, glm::dvec3 min, glm::dvec3 max) {
    return glm::dvec3(((pos.x < min.x) ? min.x : ((pos.x > max.x) ? max.x : pos.x)), ((pos.y < min.y) ? min.y : ((pos.y > max.y) ? max.y : pos.y)), ((pos.z < min.z) ? min.z : ((pos.z > max.z) ? max.z : pos.z)));
}
__device__ double clamp(double pos, double max) {
    return clamp(pos, 0, max);
}
__device__ glm::dvec2 clamp(glm::dvec2 pos, glm::dvec2 max) {
    return clamp(pos, glm::dvec2(0), max);
}
__device__ glm::dvec3 clamp(glm::dvec3 pos, glm::dvec3 max) {
    return clamp(pos, glm::dvec3(0), max);
}
__device__ double wraparound(double pos, double max) {
    return ((pos < 0) ? (max + pos) : ((pos >= max) ? (pos - max) : pos));
}
__device__ glm::dvec2 wraparound(glm::dvec2 pos, glm::dvec2 max) {
    return glm::dvec2(((pos.x < 0) ? (max.x + pos.x) : ((pos.x >= max.x) ? (pos.x - max.x) : pos.x)), ((pos.y < 0) ? (max.y + pos.y) : ((pos.y >= max.y) ? (pos.y - max.y) : pos.y)));
}
__device__ glm::dvec3 wraparound(glm::dvec3 pos, glm::dvec3 max) {
    return glm::dvec3(((pos.x < 0) ? (max.x + pos.x) : ((pos.x >= max.x) ? (pos.x - max.x) : pos.x)), ((pos.y < 0) ? (max.y + pos.y) : ((pos.y >= max.y) ? (pos.y - max.y) : pos.y)), ((pos.z < 0) ? (max.z + pos.z) : ((pos.z >= max.z) ? (pos.z - max.z) : pos.z)));
}
__device__ bool is_inside(glm::dvec2 pos, glm::dvec2 max) {
    return ((((pos.x >= 0) && (pos.y >= 0)) && (pos.x <= max.x)) && (pos.y <= max.y));
}
__device__ int calc_max_env_sugar_level(int x, int y) {
    int gmax = global_max_env_sugar_level;
    glm::dvec2 pos = glm::dvec2(x, y);
    int max = 0;
    double d1 = glm::distance(pos, glm::dvec2(63.0, 63.0));
    max += ((double) gmax * exp((((-d1) * d1) / (2.0 * sugar_variance))));
    double d2 = glm::distance(pos, glm::dvec2(189.0, 189.0));
    max += ((double) gmax * exp((((-d2) * d2) / (2.0 * sugar_variance))));
    return max;
}
__FLAME_GPU_FUNC__ int metabolise_and_growback(xmachine_memory_Agent* in) {
    glm::dvec2 in_pos = glm::dvec2(in->x, in->y);
    glm::dvec2 in_target_pos = glm::dvec2(in->target_pos_x, in->target_pos_y);
    int new_env_sugar_level = in->env_sugar_level;
    if ((in->state == AGENT_STATE_OCCUPIED)) {
        int new_sugar_level = ((in->sugar_level + in->env_sugar_level) - in->metabolism);
        new_env_sugar_level = 0;
        if ((new_sugar_level <= 0)) {
            in->state = AGENT_STATE_UNOCCUPIED;
            in->agent_id = (-1);
            in->sugar_level = 0;
            in->metabolism = 0;
        } else {
            in->state = AGENT_STATE_MOVEMENT_UNRESOLVED;
            in->sugar_level = new_sugar_level;
        }
    }
    new_env_sugar_level += SUGAR_GROWBACK_RATE;
    if ((new_env_sugar_level > in->max_env_sugar_level)) {
        new_env_sugar_level = in->max_env_sugar_level;
    }
    in->env_sugar_level = new_env_sugar_level;
    return 0;
}

__FLAME_GPU_FUNC__ int movement_request_gen(xmachine_memory_Agent* xmemory, xmachine_message_movement_request_message_list* movement_request_message_messages) {
    add_movement_request_message_message(movement_request_message_messages, xmemory->x, xmemory->y, xmemory->z, xmemory->state, xmemory->env_sugar_level);
    return 0;
}

__FLAME_GPU_FUNC__ int movement_request(xmachine_memory_Agent* in, xmachine_message_movement_request_message_list* movement_request_message_messages, xmachine_message_movement_request_message_PBM* partition_matrix) {
    glm::dvec2 in_pos = glm::dvec2(in->x, in->y);
    glm::dvec2 in_target_pos = glm::dvec2(in->target_pos_x, in->target_pos_y);
    if ((in->state == AGENT_STATE_MOVEMENT_UNRESOLVED)) {
        int best_sugar_level = (-1);
        glm::dvec2 best_pos = glm::dvec2(0);
        xmachine_message_movement_request_message* movement_request_message_message;
        for (
            movement_request_message_message = get_first_movement_request_message_message(movement_request_message_messages, partition_matrix, in->x, in->y, in->z);
            movement_request_message_message;
            movement_request_message_message = get_next_movement_request_message_message(movement_request_message_message, movement_request_message_messages, partition_matrix)
        ) {
            glm::dvec2 nx_pos = glm::dvec2(movement_request_message_message->x, movement_request_message_message->y);
            if (glm::distance(nx_pos, in_pos) >= radius) continue;
            {
                if ((nx_pos == in_pos)) continue;
                if (((movement_request_message_message->state == AGENT_STATE_UNOCCUPIED) && (movement_request_message_message->env_sugar_level > best_sugar_level))) {
                    best_sugar_level = movement_request_message_message->env_sugar_level;
                    best_pos = nx_pos;
                }
            }
        }
        if ((best_sugar_level > in->env_sugar_level)) {
            in->state = AGENT_STATE_MOVEMENT_REQUESTED;
            in->target_pos_x = best_pos.x;
            in->target_pos_y = best_pos.y;
            
        } else {
            in->state = AGENT_STATE_OCCUPIED;
        }
    }
    return 0;
}

__FLAME_GPU_FUNC__ int movement_response_gen(xmachine_memory_Agent* xmemory, xmachine_message_movement_response_message_list* movement_response_message_messages) {
    add_movement_response_message_message(movement_response_message_messages, xmemory->x, xmemory->y, xmemory->z, xmemory->target_pos_x, xmemory->target_pos_y, xmemory->agent_id, xmemory->state, xmemory->sugar_level, xmemory->metabolism);
    return 0;
}

__FLAME_GPU_FUNC__ int movement_response(xmachine_memory_Agent* in, xmachine_message_movement_response_message_list* movement_response_message_messages, xmachine_message_movement_response_message_PBM* partition_matrix) {
    glm::dvec2 in_pos = glm::dvec2(in->x, in->y);
    glm::dvec2 in_target_pos = glm::dvec2(in->target_pos_x, in->target_pos_y);
    if ((in->state == AGENT_STATE_UNOCCUPIED)) {
        int best_priority = (-1);
        int best_agent_id = (-1);
        int best_sugar_level = (-1);
        int best_metabolism = (-1);
        xmachine_message_movement_response_message* movement_response_message_message;
        for (
            movement_response_message_message = get_first_movement_response_message_message(movement_response_message_messages, partition_matrix, in->x, in->y, in->z);
            movement_response_message_message;
            movement_response_message_message = get_next_movement_response_message_message(movement_response_message_message, movement_response_message_messages, partition_matrix)
        ) {
            glm::dvec2 nx_pos = glm::dvec2(movement_response_message_message->x, movement_response_message_message->y);
            glm::dvec2 nx_target_pos = glm::dvec2(movement_response_message_message->target_pos_x, movement_response_message_message->target_pos_y);
            if (glm::distance(nx_pos, in_pos) >= radius) continue;
            {
                if (((movement_response_message_message->state == AGENT_STATE_MOVEMENT_REQUESTED) && (nx_target_pos == in_pos))) {
                    int message_priority = 0;
                    if ((message_priority > best_priority)) {
                        best_priority = message_priority;
                        best_agent_id = movement_response_message_message->agent_id;
                        best_sugar_level = movement_response_message_message->sugar_level;
                        best_metabolism = movement_response_message_message->metabolism;
                    }
                }
            }
        }
        if ((best_agent_id >= 0)) {
            in->state = AGENT_STATE_OCCUPIED;
            in->agent_id = best_agent_id;
            in->sugar_level = best_sugar_level;
            in->metabolism = best_metabolism;
        }
    }
    return 0;
}

__FLAME_GPU_FUNC__ int movement_transaction_gen(xmachine_memory_Agent* xmemory, xmachine_message_movement_transaction_message_list* movement_transaction_message_messages) {
    add_movement_transaction_message_message(movement_transaction_message_messages, xmemory->x, xmemory->y, xmemory->z, xmemory->agent_id, xmemory->state);
    return 0;
}

__FLAME_GPU_FUNC__ int movement_transaction(xmachine_memory_Agent* in, xmachine_message_movement_transaction_message_list* movement_transaction_message_messages, xmachine_message_movement_transaction_message_PBM* partition_matrix) {
    glm::dvec2 in_pos = glm::dvec2(in->x, in->y);
    glm::dvec2 in_target_pos = glm::dvec2(in->target_pos_x, in->target_pos_y);
    if ((in->state == AGENT_STATE_MOVEMENT_REQUESTED)) {
        bool moved = false;
        xmachine_message_movement_transaction_message* movement_transaction_message_message;
        for (
            movement_transaction_message_message = get_first_movement_transaction_message_message(movement_transaction_message_messages, partition_matrix, in->x, in->y, in->z);
            movement_transaction_message_message;
            movement_transaction_message_message = get_next_movement_transaction_message_message(movement_transaction_message_message, movement_transaction_message_messages, partition_matrix)
        ) {
            glm::dvec2 nx_pos = glm::dvec2(movement_transaction_message_message->x, movement_transaction_message_message->y);
            if (glm::distance(nx_pos, in_pos) >= radius) continue;
            {
                if (((movement_transaction_message_message->state == AGENT_STATE_OCCUPIED) && (movement_transaction_message_message->agent_id == in->agent_id))) {
                    moved = true;
                    in->state = AGENT_STATE_UNOCCUPIED;
                    in->agent_id = (-1);
                    in->sugar_level = 0;
                    in->metabolism = 0;
                }
            }
        }
        if ((!moved)) {
            in->state = AGENT_STATE_OCCUPIED;
        }
    }
    return 0;
}

#endif // #ifndef _FUNCTIONS_H
