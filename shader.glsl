#define N 100
#define OBJS 13

// x, y position of the light
uniform vec2 lightPosition;
uniform vec2 lightPosition2;
// Size of light in pixels
uniform float lightSize;

// objetos que emitem luz
uniform vec2 light_1;
uniform vec2 light_2;
uniform vec2 light_3;
uniform vec2 light_4;
uniform vec2 light_5;
uniform vec2 light_6;
uniform vec2 light_7;
uniform vec2 light_8;
uniform vec2 light_9;
uniform vec2 light_10;
uniform vec2 light_11;
uniform vec2 light_12;
uniform vec2 light_13;

// intensidade das luzes
uniform float light_size_1;
uniform float light_size_2;
uniform float light_size_3;
uniform float light_size_4;
uniform float light_size_5;
uniform float light_size_6;
uniform float light_size_7;
uniform float light_size_8;
uniform float light_size_9;
uniform float light_size_10;
uniform float light_size_11;
uniform float light_size_12;
uniform float light_size_13;


// basicamente verificando as paredes do chanel0
float terrain(vec2 samplePoint)
{
    float samplePointAlpha = texture(iChannel0, samplePoint).a;
    float sampleStepped = step(0.1, samplePointAlpha);
    float returnValue = 1.0 - sampleStepped;
    return returnValue;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{

    // coloca tudo em vetores
    vec2 lights[OBJS];
    lights[0] = light_1;
    lights[1] = light_2;
    lights[2] = light_3;
    lights[3] = light_4;
    lights[4] = light_5;
    lights[5] = light_6;
    lights[6] = light_7;
    lights[7] = light_8;
    lights[8] = light_9;
    lights[9] = light_10;
    lights[10] = light_11;
    lights[11] = light_12;
    lights[12] = light_13;

    float light_sizes[OBJS];
    light_sizes[0] = light_size_1;
    light_sizes[1] = light_size_2;
    light_sizes[2] = light_size_3;
    light_sizes[3] = light_size_4;
    light_sizes[4] = light_size_5;
    light_sizes[5] = light_size_6;
    light_sizes[6] = light_size_7;
    light_sizes[7] = light_size_8;
    light_sizes[8] = light_size_9;
    light_sizes[9] = light_size_10;
    light_sizes[10] = light_size_11;
    light_sizes[11] = light_size_12;
    light_sizes[12] = light_size_13;


    float distances_light[OBJS];
    vec2 normalized_light_coords[OBJS];

    for (int i = 0; i < OBJS; i++) {
        distances_light[i] = length(lights[i] - fragCoord);
    }

    // Distância do pixel para as luzes (so preciso calcular as coisas de cada luz por pixel se o tem chance de ser iluminado)
    // float distanceToLight = length(lightPosition - fragCoord);
    // float distanceToLight2 = length(lightPosition2 - fragCoord);

    // Normalize the fragment coordinate from (0.0, 0.0) to (1.0, 1.0)
    vec2 normalizedFragCoord = fragCoord/iResolution.xy;

    for (int i = 0; i < OBJS; i++) {
        normalized_light_coords[i] = lights[i].xy/iResolution.xy;
    }    
    // vec2 normalizedLightCoord = lightPosition.xy/iResolution.xy;
    // vec2 normalizedLight2Coord = lightPosition2.xy/iResolution.xy;

    float light_amount[OBJS];
    for (int i = 0; i < OBJS; i++) {
        light_amount[i] = 0;
    }

    for (int j = 0; j < OBJS; j++) {
        if (distances_light[j] <= light_sizes[j]) {
            light_amount[j] = 1.0;
            for(float i = 0.0; i < N; i++)
            {
                // A 0.0 - 1.0 ratio between where our current pixel is, and where the light is
                float t = i / N;
                // Grab a coordinate between where we are and the light
                vec2 samplePoint = mix(normalizedFragCoord, normalized_light_coords[j], t);
                // Is there something there? If so, we'll assume we are in shadow
                float shadowAmount = terrain(samplePoint);
                // Multiply the light amount.
                // (Multiply in case we want to upgrade to soft shadows)
                light_amount[j] *= shadowAmount;
            }
            light_amount[j] *= 1.0 - smoothstep(0.0, light_sizes[j], distances_light[j]);
        }
    }

    float light_sum = 0;
    for (int i = 0; i < OBJS; i++) {
        light_sum += light_amount[i];
    }

    // We'll alternate our display between black and whatever is in channel 1
    vec4 blackColor = vec4(0.0, 0.0, 0.0, 1.0);

    // Our fragment color will be somewhere between black and channel 1
    // dependent on the value of b.
    fragColor = mix(blackColor, texture(iChannel1, normalizedFragCoord), light_sum);
}
