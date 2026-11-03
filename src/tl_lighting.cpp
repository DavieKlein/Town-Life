#include "tl_lighting.h"

namespace tl
{
    namespace
    {
        struct keyframe
        {
            int minutes;
            light_params params;
        };

        //                            mul r/g/b        add r/g/b  sat  night
        constexpr light_params night_light = { 97, 108, 160,   0, 0, 1,   150, 256 };
        constexpr light_params dawn_light = { 215, 190, 205,   2, 0, 1,   215, 120 };
        constexpr light_params day_light = { 256, 256, 256,   0, 0, 0,   256, 0 };
        constexpr light_params golden_light = { 272, 222, 180,   1, 0, 0,   235, 0 };
        constexpr light_params dusk_light = { 160, 140, 190,   1, 0, 1,   185, 170 };

        constexpr keyframe keyframes[] = {
            { 0, night_light },
            { 5 * 60, night_light },
            { 6 * 60 + 15, dawn_light },
            { 7 * 60 + 30, day_light },
            { 17 * 60, day_light },
            { 18 * 60 + 30, golden_light },
            { 19 * 60 + 40, dusk_light },
            { 20 * 60 + 40, night_light },
            { 24 * 60, night_light },
        };

        [[nodiscard]] int mix(int a, int b, int t, int range)
        {
            return a + (((b - a) * t) / range);
        }

        [[nodiscard]] int clamp31(int value)
        {
            return value < 0 ? 0 : (value > 31 ? 31 : value);
        }

        [[nodiscard]] bn::color mix_colour(bn::color a, bn::color b, int t)   // t in 0..256
        {
            return bn::color(clamp31(mix(a.red(), b.red(), t, 256)), clamp31(mix(a.green(), b.green(), t, 256)),
                             clamp31(mix(a.blue(), b.blue(), t, 256)));
        }

        // Ripple shades rotate through the water entries.
        constexpr int water_frames_per_step = 10;

        // Lit window glass (dark, bright) and lamp glass at night.
        constexpr bn::color lit_glass[2] = { bn::color(28, 21, 9), bn::color(31, 28, 17) };
        constexpr bn::color lit_lamp(31, 31, 24);
    }

    light_params lighting_at(int minutes, bool outdoor)
    {
        if(! outdoor)
        {
            return day_light;
        }

        minutes %= 24 * 60;

        for(int index = 1; index < int(sizeof(keyframes) / sizeof(keyframe)); ++index)
        {
            const keyframe& b = keyframes[index];

            if(minutes <= b.minutes)
            {
                const keyframe& a = keyframes[index - 1];
                int t = minutes - a.minutes;
                int range = b.minutes - a.minutes;
                light_params result;
                result.mul_r = mix(a.params.mul_r, b.params.mul_r, t, range);
                result.mul_g = mix(a.params.mul_g, b.params.mul_g, t, range);
                result.mul_b = mix(a.params.mul_b, b.params.mul_b, t, range);
                result.add_r = mix(a.params.add_r, b.params.add_r, t, range);
                result.add_g = mix(a.params.add_g, b.params.add_g, t, range);
                result.add_b = mix(a.params.add_b, b.params.add_b, t, range);
                result.sat = mix(a.params.sat, b.params.sat, t, range);
                result.night = mix(a.params.night, b.params.night, t, range);
                return result;
            }
        }

        return night_light;
    }

    bn::color light_colour(bn::color colour, const light_params& p)
    {
        int r = colour.red();
        int g = colour.green();
        int b = colour.blue();

        if(p.sat != 256)
        {
            int grey = (r + g + b) / 3;
            r = grey + (((r - grey) * p.sat) >> 8);
            g = grey + (((g - grey) * p.sat) >> 8);
            b = grey + (((b - grey) * p.sat) >> 8);
        }

        r = ((r * p.mul_r) >> 8) + p.add_r;
        g = ((g * p.mul_g) >> 8) + p.add_g;
        b = ((b * p.mul_b) >> 8) + p.add_b;
        return bn::color(clamp31(r), clamp31(g), clamp31(b));
    }

    void light_colours(const bn::color* source, bn::color* destination, int count, const light_params& params)
    {
        for(int index = 0; index < count; ++index)
        {
            destination[index] = light_colour(source[index], params);
        }
    }

    void light_layer(const layer_data& layer, bn::color* destination, const light_params& params, int water_phase)
    {
        int count = layer.banks * 16;
        light_colours(layer.palette, destination, count, params);

        int lit = params.night <= 96 ? 0 : (params.night >= 224 ? 256 : ((params.night - 96) * 2));
        int step = water_phase / water_frames_per_step;

        for(int bank = 0; bank < layer.banks; ++bank)
        {
            const bn::color* source = layer.palette + (bank * 16);
            bn::color* target = destination + (bank * 16);

            if(layer.glass_first)
            {
                for(int index = 0; index < 2; ++index)
                {
                    int entry = layer.glass_first + index;
                    target[entry] = mix_colour(target[entry], lit_glass[index], lit);
                }
            }

            if(layer.lamp_index)
            {
                target[layer.lamp_index] = mix_colour(target[layer.lamp_index], lit_lamp, lit);
            }

            if(layer.water_count && (layer.water_banks & (1 << bank)))
            {
                int n = layer.water_count;

                for(int index = 0; index < n; ++index)
                {
                    int from = layer.water_first + ((index + step) % n);
                    target[layer.water_first + index] = light_colour(source[from], params);
                }
            }
        }
    }
}
