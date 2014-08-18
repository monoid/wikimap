var map, mc, windowFeed, icons;

function _(str) {
    return gettext(str);
}

// BEGIN DJANGO CSRF
// From https://docs.djangoproject.com/en/1.6/ref/contrib/csrf/#ajax
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
// END OF DJANGO CSRF

function zoomGhStr(zoom, pt) {
    return GX._tr.charAt(zoom)+GX.encode(pt.lat(), pt.lng(), 16+2*zoom);
}

function createButton(label, action) {
    var jbutton = $('<div class="fmcontrol"></div>').text(label);
    jbutton.click(action);

    return jbutton.get(0);
}


function whoSThereControl() {
    var jpane = $('#srchoutput');

    return createButton(_("Кто здесь?.."), (function () {
        //map.savePosition();
        var ext = map.getBounds(), i, ul = $('<ul class="srchres"></ul>');
        var points = [];
        jpane.empty();
        for (i = 0; i < icons.length; ++i) {
            var pt, gh;
            if (ext.contains(pt = icons[i].position)) {
                (function (m, pt, zoom) {
                    points.push($('<li></li>')
                                   .append($('<a></a>')
                                   .attr('href', '#'+zoomGhStr(zoom, pt))
                                   .text(icons[i].getTitle())
                                   .click(function (evt) {
                                       map.setCenter(pt, zoom);
                                       clickListener.call(m, evt);
                                       evt.stopPropagation();

                                       return true;
                                     })
                                    )
                                   .append($('<br></br>'))
                                   .append($('<span></span>').text(deg2hms(pt.lat())
                                                                   +' '
                                                                   +deg2hms(pt.lng()))));
                }(icons[i], pt, Number(pts[i].z)));
            }
        }
        ul.append(points);
        jpane.append(ul.length
                     ? ul
                     : $('<div class="srchnthng"></div>').text(
                         _("Ничего не найдено...")));
        $("#srchspace").fadeIn("fast");
    }));
}

function loginLogout() {
    var label, url;
    if (auth) {
        label = _("Выход");
        url = 'logout';
    } else {
        label = _("Вход");
        url = 'login';
    }
    return createButton(label, function () {
        location.replace(url);
    });
}

function trim(str) {
    return str.replace(/(^\s+)|(\s+$)/g, "");
}

function deg2hms(deg) {
    var h = Math.floor(deg);
    deg = 60*(deg - h);
    var m = Math.floor(deg);
    deg = 60*(deg - m);
    var s = Math.floor(deg);

    return String(h)+'°'+m+"'"+s+'"';
}

function addPoint(pt, form) {
    closeInfoWindow();
    var txt = trim($('.inp', form).val());
    $.ajax({
        url: 'ajax',
        type: 'POST',
        data: {
            cmd: 'insert',
            lat: String(pt.lat()),
            lon: String(pt.lng()),
            txt: txt,
            zoom: map.getZoom()
        },
        success: function(msg) {
            try {
                if (msg.status === 'OK') {
                    var m = createMarker(map, pt, msg.id, txt, true);
                    icons.push(m);
                    mc.addMarker(m);
                    //map.addOverlay(m);
                } else {
                    // TODO Report error
                }
            } catch (e) {
                // TODO Report error
                if (window.console) {
                    window.console.debug('Exception in addPoint:', e);
                }
            }
        }
    });
    return false;
}

function updPoint(marker, form) {
    closeInfoWindow();
    var txt = trim($('.inp', form).val());
    $.ajax({
        url: 'ajax',
        type: 'POST',
        data: {
            cmd: 'updattr',
            id: marker.frid,
            txt: txt
        },
        success: function(msg) {
            var idx = jQuery.inArray(marker, icons), m;
            mc.removeMarker(marker);
            mc.addMarker(m = createMarker(map, marker.position, marker.frid, txt, true));
            if (idx >= 0) {
                icons[idx] = m;
            } else {
                icons.push(m);
            }
        }
    });
    return false;
}

function cancel() {
    closeInfoWindow();
    return false;
}

function delPoint(marker) {
    closeInfoWindow();
    marker.set('dragging', false);
    marker.set('visible', false);
    $.ajax({
        url: 'ajax',
        type: 'POST',
        data: {
            cmd: 'del',
            id: marker.frid
        },
        success: function(msg) {
            mc.removeMarker(marker);
        }
    });
    return false;
}

function createMarker(map, pt, id, txt, draggable) {
    var mark = new google.maps.Marker({
        icon: '/static/icons/circle-star.png',
        position: pt,
        title: txt,
        draggable: draggable,
        bouncy: true,
        map: map
    });
    mark.addListener('click', clickListener);
    mark.frid = id;
    if (draggable) {
        mark.addListener('dragend', dragListener);
    }
    return mark;
}


function dragListener() {
    var pt = this.position;
    $.ajax({
        url: 'ajax',
        type: 'POST',
        data: {
            cmd: 'updgeom',
            id: this.frid,
            lat: String(pt.lat()),
            lon: String(pt.lng()),
            zoom: map.getZoom()
        }
    });
    return false;
}

function keyHandler(e) {
    var code = (e.keyCode ? e.keyCode : e.which);
    if (code == 13 && e.originalTarget.tagName != 'BUTTON') {
        okFun();
    } else if (code == 27) cancel();
}


var iwin;

function createInfoWindow(pt, html) {
    if (iwin) {
	iwin.close();
    }
    iwin = new google.maps.InfoWindow({
	position: pt,
	content: html
    });
    return iwin;
}

function closeInfoWindow() {
    if (iwin) {
	iwin.close();
	iwin = null;
    }
}

function mapClickHandler(evt) {
    var pt = evt.latLng;
    // New marker
    form = $(_("<div class='req'>Ваше имя или название места:<br /></div>"))
        .append($("<input class='inp'></input>")
                .keyup(function () {
                    // Disable OK button if value is empty
                    $('.ok', form).attr('disabled', trim($(this).val()).length == 0 ? 'disabled' : null);
                }))
        .append($('<p class="coords"></p>').text(deg2hms(pt.lat())
						 +', '
						 +deg2hms(pt.lng())))
        .append($(_("<button class='ok' disabled='disabled'>OK</button>")).click(
            okFun = function() {return addPoint(pt, form);}
        )).append($(_("<button class='cancel'>Отмена</button>")).click(
            cancel
        ));
    form.bind('keypress', keyHandler);
    
    createInfoWindow(pt, form.get(0)).open(map);
    return true;
}

function clickListener(evt) {
    var marker = this, pt = evt.latLng, form, okFunc;
        // Click on marker
        if (marker.draggable) {
            pt = marker.position;
            form = $('<div></div>')
                .append($('<p class="pointid"></p>').text('#'+(marker.frid || '')))
                .append($(_("<div class='req'>Ваше имя или название места:<br /></div>")))
                .append($(_('<input class="inp"></input>'))
                        .attr('value', marker.getTitle())
                        .keyup(function () {
                            // Disable OK button if value is empty
                            $('.ok', form).attr('disabled', trim($(this).val()).length == 0 ? 'disabled' : null);
                        }))
                .append($('<p class="coords"></p>').text(deg2hms(pt.lat())
                                          +', '
                                          +deg2hms(pt.lng())))
                .append($(_("<button class='ok'>OK</button>")).click(
                    okFun = function() {return updPoint(marker, form);}
                )).append($(_("<button class='del'>Удалить</button>")).click(
                    function() {return delPoint(marker);}
                )).append($(_("<button class='cancel'>Отмена</button>")).click(
                    cancel
                ));
            form.bind('keypress', keyHandler);
            createInfoWindow(pt, form.get(0)).open(map);
        } else if (marker.position) {
            var title = marker.getTitle();
            pt = marker.position;
	    createInfoWindow(pt, $('<div class="usercard"></div>')
                                  .append($('<p class="pointid"></p>').text('#'+(marker.frid || '')))
                                  .append($('<h3></h3>').text(title))
                                  .append($('<p class="coords"></p>').text(deg2hms(pt.lat())
                                                            +', '
                                                            +deg2hms(pt.lng())))
                             .get(0)).open(map, marker); 
        }
    return false;
}

function anchorChanged(map) {
    var anchor = window.location.href.split("#").pop();
    if (anchor.length > 1 && GX.checkValid(anchor.substr(1)) && GX._tr.indexOf(anchor.charAt(0)) >= 0) {
        var zoom=GX._tr.indexOf(anchor.charAt(0));
        var gx = GX.decode(anchor.substr(1));
        map.set('center', new google.maps.LatLng(gx.lat, gx.lon));
        map.set('zoom', zoom);
        return true;
    } else {
        return false;
    }
}

function showMessages() {
    var m = $('#messagebox');
    var c = $('#messagebox-close');
    if ($('#messagebox-body').children().length > 0) {
        $('#messagebox').show();
        c.click(function () {
            m.hide();
        });
    }
}
function load() {
    showMessages();
    google.maps.visualRefresh = true;
    var container = document.getElementById("map");
    var cfg = {
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    if (type == 'compact') {
        cfg.mapTypeControl = true;
        cfg.scaleControl = true;
    } else {
        cfg.mapTypeControl = true;
        cfg.scaleControl = true;
        cfg.overviewMapControl = true;
    }        
    map = new google.maps.Map(container, cfg);

    // if (type == 'compact') {
    //     map.addControl(new GSmallMapControl());
    //     map.addControl(new GMenuMapTypeControl());
    // } else {
    //     map.addControl(new GLargeMapControl());
    //     map.addControl(new GMapTypeControl());
    //     map.addControl(new GScaleControl());
    //     map.addControl(new GOverviewMapControl());
    //     map.addControl(new WhoSThereControl());
    // }
    icons = Array(pts.length);


//         windowFeed = $('<link rel="alternate" type="application/atom+xml" title="Atom Feed of New Points in current View"></link>');
//         $("head").append(windowFeed);
        
    function onMove() {
        var zoom = map.get('zoom');
        var center = map.get('center');
        var lnk = '#'+GX._tr.charAt(zoom)+GX.encode(center.lat(), center.lng(), 16+2*zoom);
        window.location.href = lnk;
    }
    
    map.addListener('click', mapClickHandler);
    map.addListener('bounds_changed', onMove);
    $(window).resize(function () { google.maps.event.trigger(map, 'resize'); });

    if (!anchorChanged(map)) {
        if (window['extent'] == 'russia') {
            map.set('center', new google.maps.LatLng(59.95, 95));
            map.set('zoom', 3);
        } else if (window['extent'] == 'world') {
            map.set('center', new google.maps.LatLng(0.0, 0.0));
            map.set('zoom', 2);
        } else {
            map.set('center', new google.maps.LatLng(54.95, 83));
            map.set('zoom', 10);
        }
    }

    var mcOptions = {gridSize: 20, maxZoom: 15};
    mc = new MarkerClusterer(map, [], mcOptions);

    var i = 0;
    function batchAddMarker() {
        for (var j = 0; j < 100 && i < pts.length; ++j, ++i) {
            var p = pts[i], lat, lon, m;
            if (p.pt == null) {
                continue;
            } else if (GX.checkValid(p.pt)) {
            // WKT point is never valid GeoHash as it contains OI and ()
                var d = GX.decode(p.pt);
                lat = d.lat;
                lon = d.lon;
            } else if ((m = p.pt.match(/POINT\(([^ ]*) ([^)]*)\)$/i))) {
                lat = Number(m[1]);
                lon = Number(m[2]);
            }
            icons[i] = createMarker(map,
                                    new google.maps.LatLng(lat, lon),
                                    p.id,
                                    p.title,
                                    p.drag == "1");
            mc.addMarker(icons[i]);
        }
        if (i < pts.length) {
            setTimeout(batchAddMarker, 10);
        } else {
            // All points are added, it's time to add controls
            var wt = whoSThereControl();
            wt.index = 1;

            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(wt);

            var ll = loginLogout();
            ll.index = 2;
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push(ll);
        }
    }
    setTimeout(batchAddMarker, 10);

    $('#srchclose').click(function () {
            $("#srchspace").fadeOut("fast");
    });

    $(window).on('hashchange', function () {
        anchorChanged(map);
    });
}

/* (C) 2009 Ivan Boldyrev
 * GX is a fast Geohash library in JavaScript.
 */

window['GX'] = {
    decode: function (str) {
        /* Strings longer 12 chars will lead to 32bit int overflow, but
           precision is more than necessary.
         */
        str = str.substr(0, 11);
        var l = str.length, i, l1=0, l2=0, ll1=0, ll2=0, al1, al2, c, i1;
        for (i=0; i<l; ++i) {
            c = GX._tr.indexOf(str.charAt(i));
            i1 = i&1;
            ll1 += (al1 = 3-i1);
            ll2 += (al2 = 2+i1);
            l1 = (l1 << al1) + GX._dm[c>>i1];
            l2 = (l2 << al2) + GX._dm[c>>(1-i1)];
        }
        l1 = l1/Math.pow(2.0, ll1) - 0.5;
        l2 = l2/Math.pow(2.0, ll2) - 0.5;
        return {lat:  180.0*l2, lon: 360.0*l1};
    },

    encode: function (lat, lon, bits) {

        lat = lat/180.0+0.5;
        lon = lon/360.0+0.5;

        /* We generate two symbols per iteration; each symbol is 5
         * bits; so we divide by 2*5 == 10.
         */
        var r = '', l = Math.ceil(bits/10), hlt, hln, b2, hi, lo, i;

        for (i = 0; i < l; ++i) {
            lat *= 0x20;
            lon *= 0x20;

            hlt = Math.min(0x1F, Math.floor(lat));
            hln = Math.min(0x1F, Math.floor(lon));

            lat -= hlt;
            lon -= hln;

            b2 = GX._sparse(hlt) | (GX._sparse(hln) << 1);

            hi = b2 >> 5;
            lo = b2 & 0x1F;

            r += GX._tr.charAt(hi) + GX._tr.charAt(lo);
        }

        r = r.substr(0, Math.ceil(bits/5));
        return r;
    },

    checkValid: function(str) {
        return str && !!str.match(/^[0-9b-hjkmnp-z]+$/);
    },

    _tr: "0123456789bcdefghjkmnpqrstuvwxyz",
    /* This is a table of i => "even bits of i combined".  For example:
     * #b10101 => #b111
     * #b01111 => #b011
     * #bABCDE => #bACE
     */
    _dm: [0, 1, 0, 1, 2, 3, 2, 3, 0, 1, 0, 1, 2, 3, 2, 3,
          4, 5, 4, 5, 6, 7, 6, 7, 4, 5, 4, 5, 6, 7, 6, 7],

    /* This is an opposit of _tr table: it maps #bABCDE to
     * #bA0B0C0D0E.
     */
    _dr: [0, 1, 4, 5, 16, 17, 20, 21, 64, 65, 68, 69, 80,
          81, 84, 85, 256, 257, 260, 261, 272, 273, 276, 277,
          320, 321, 324, 325, 336, 337, 340, 341],

    _sparse: function (val) {
        var acc = 0, off = 0;

        while (val > 0) {
            low = val & 0xFF;
            acc |= GX._dr[low] << off;
            val >>= 8;
            off += 16;
        }
        return acc;
    }
};
