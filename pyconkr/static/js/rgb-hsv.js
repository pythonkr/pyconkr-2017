function RgbToHsv(rgb) {
    var min = Math.min(rgb.r, rgb.g, rgb.b),
        max = Math.max(rgb.r, rgb.g, rgb.b),
        delta = max - min,
        h, s, v = max;

    v = Math.floor(max / 255 * 100);
    if (max == 0) return {h:0, s:0, v:0, a:rgb.a};
    s = Math.floor(delta / max * 100);
    var deltadiv = delta == 0 ? 1 : delta;
    if( rgb.r == max ) h = (rgb.g - rgb.b) / deltadiv;
    else if(rgb.g == max) h = 2 + (rgb.b - rgb.r) / deltadiv;
    else h = 4 + (rgb.r - rgb.g) / deltadiv;
    h = Math.floor(h * 60);
    if( h < 0 ) h += 360;
    return { h: h, s:s, v:v, a:rgb.a }
}

function HsvToRgb(hsv) {
    h = hsv.h / 360;
    s = hsv.s / 100;
    v = hsv.v / 100;
    
    if (s == 0)
    {
        var val = Math.round(v * 255);
        return {r:val,g:val,b:val,a:hsv.a};
    }
    hPos = h * 6;
    hPosBase = Math.floor(hPos);
    base1 = v * (1 - s);
    base2 = v * (1 - s * (hPos - hPosBase));
    base3 = v * (1 - s * (1 - (hPos - hPosBase)));
    if (hPosBase == 0) {red = v; green = base3; blue = base1}
    else if (hPosBase == 1) {red = base2; green = v; blue = base1}
    else if (hPosBase == 2) {red = base1; green = v; blue = base3}
    else if (hPosBase == 3) {red = base1; green = base2; blue = v}
    else if (hPosBase == 4) {red = base3; green = base1; blue = v}
    else {red = v; green = base1; blue = base2};
        
    red = Math.round(red * 255);
    green = Math.round(green * 255);
    blue = Math.round(blue * 255);
    return {r:red,g:green,b:blue,a:hsv.a};
} 

function mixRgb(color1, color2, amount) 
{
    var hsv1 = RgbToHsv(color1);
    var hsv2 = RgbToHsv(color2);

    var h = amount * hsv2.h + (1.0 - amount) * hsv1.h;
    var s = amount * hsv2.s + (1.0 - amount) * hsv1.s;
    var v = amount * hsv2.v + (1.0 - amount) * hsv1.v;
    var a = amount * hsv2.a + (1.0 - amount) * hsv1.a;

    return HsvToRgb({h:h, s:s, v:v, a:a});
}

function getSkyColorAt(hour, minute)
{
    var skyCode = [
        [{r: 38, g: 37, b: 51, a: 0.9}, {r:  0, g:  0, b:  0, a: 1.0}],
        [{r:  0, g:  0, b:  0, a: 0.5}, {r:  0, g:  0, b:  0, a: 0.9}],
        [{r: 75, g: 83, b: 92, a: 1.0}, {r:131, g:177, b:224, a: 1.0}],
        [{r:130, g:175, b:224, a: 1.0}, {r: 60, g:203, b:226, a: 1.0}],
        [{r:112, g:216, b:239, a: 1.0}, {r:198, g:180, b:220, a: 1.0}],
        [{r:112, g:163, b:239, a: 1.0}, {r:202, g:142, b:198, a: 1.0}],
        [{r: 88, g: 81, b:197, a: 1.0}, {r:230, g:105, b:145, a: 1.0}],
        [{r: 43, g: 28, b: 58, a: 1.0}, {r: 84, g: 18, b: 39, a: 1.0}]
    ];

    var begin = Math.floor(hour/3);
    var end = (begin + 1) % 8;
    var mix = (hour - begin * 3) * 0.33 + (minute / 60.0 / 3.0);

    var color = skyCode[begin][0];
    var from = mixRgb(skyCode[begin][0], skyCode[end][0], mix);
    var to = mixRgb(skyCode[begin][1], skyCode[end][1], mix);

    var css = "linear-gradient(to bottom, "
        + "rgba("+from.r+","+from.g+","+from.b+","+from.a+") 0%, "
        + "rgba("+to.r+","+to.g+","+to.b+","+to.a+") 100%)";

    return css
}
