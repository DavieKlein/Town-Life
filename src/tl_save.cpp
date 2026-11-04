#include "tl_save.h"

#include <stddef.h>

#include "bn_sram.h"

namespace tl
{
    namespace
    {
        [[nodiscard]] uint32_t checksum_of(const save_data& data)
        {
            const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&data);
            uint32_t a = 1;
            uint32_t b = 0;

            for(int index = int(offsetof(save_data, map)); index < int(sizeof(save_data)); ++index)
            {
                a = (a + bytes[index]) % 65521;
                b = (b + a) % 65521;
            }

            return (b << 16) | a;
        }
    }

    bool save_read(save_data& out)
    {
        static save_data buffer;        // too big for the stack
        bn::sram::read(buffer);

        if(buffer.magic != save_data::magic_value || buffer.version != save_data::save_version ||
           buffer.size != sizeof(save_data) || buffer.checksum != checksum_of(buffer))
        {
            return false;
        }

        if(buffer.map >= maps_count || buffer.minutes >= 24 * 60 || buffer.facing > 7)
        {
            return false;
        }

        out = buffer;
        return true;
    }

    void save_write(save_data& data)
    {
        data.magic = save_data::magic_value;
        data.version = save_data::save_version;
        data.size = sizeof(save_data);
        data.checksum = checksum_of(data);
        bn::sram::write(data);
    }
}
