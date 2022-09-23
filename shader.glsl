#define N 100
#define OBJS 4

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

// intensidade das luzes
uniform float light_size_1;
uniform float light_size_2;
uniform float light_size_3;
uniform float light_size_4;


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

    float light_sizes[OBJS];
    light_sizes[0] = light_size_1;
    light_sizes[1] = light_size_2;
    light_sizes[2] = light_size_3;
    light_sizes[3] = light_size_4;


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

    // // Start our mixing variable at 1.0
    // float lightAmount = 1.0;
    // for(float i = 0.0; i < N; i++)
    // {
    //     // A 0.0 - 1.0 ratio between where our current pixel is, and where the light is
    //     float t = i / N;
    //     // Grab a coordinate between where we are and the light
    //     vec2 samplePoint = mix(normalizedFragCoord, normalizedLightCoord, t);
    //     // Is there something there? If so, we'll assume we are in shadow
	//     float shadowAmount = terrain(samplePoint);
    //     // Multiply the light amount.
    //     // (Multiply in case we want to upgrade to soft shadows)
    //     lightAmount *= shadowAmount;
    // }
    // lightAmount *= 1.0 - smoothstep(0.0, lightSize, distanceToLight);

    
    // float lightAmount2 = 1.0;
    // for(float i = 0.0; i < N; i++)
    // {
    //     // A 0.0 - 1.0 ratio between where our current pixel is, and where the light is
    //     float t = i / N;
    //     // Grab a coordinate between where we are and the light
    //     vec2 samplePoint = mix(normalizedFragCoord, normalizedLight2Coord, t);
    //     // Is there something there? If so, we'll assume we are in shadow
	//     float shadowAmount = terrain(samplePoint);
    //     // Multiply the light amount.
    //     // (Multiply in case we want to upgrade to soft shadows)
    //     lightAmount2 *= shadowAmount;
    // }
    // lightAmount2 *= 1.0 - smoothstep(0.0, lightSize, distanceToLight2);

    // We'll alternate our display between black and whatever is in channel 1
    vec4 blackColor = vec4(0.0, 0.0, 0.0, 1.0);

    // Our fragment color will be somewhere between black and channel 1
    // dependent on the value of b.
    fragColor = mix(blackColor, texture(iChannel1, normalizedFragCoord), light_sum);
}
