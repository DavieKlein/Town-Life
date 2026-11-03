#include "tl_world.h"

#include "tl_world_data.h"

namespace tl
{
    static_assert(sizeof(world_data::maps) / sizeof(map_info) == maps_count);

    const map_info& get_map(map_id id)
    {
        return world_data::maps[int(id)];
    }
}
