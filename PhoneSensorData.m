%% Live phyphox inclination acquisition
clear; clc;

% -------- User settings --------
baseUrl  = "http://172.20.10.1";   % <-- replace with your phone's phyphox URL
duration = 5;                           % seconds to run
dt       = 0.1;                          % polling interval in seconds

% Buffers you want
bufT  = "t";
bufLR = "tiltFlatLR";    % left/right
bufUD = "tiltFlatUD";    % vertical (up/down)

% -------- Make sure remote interface is reachable --------
cfg = webread(baseUrl + "/config", weboptions("ContentType","json","Timeout",5));
disp("Connected to: " + string(cfg.title))

% -------- Reset and start experiment --------
webread(baseUrl + "/control?cmd=clear", weboptions("ContentType","json","Timeout",5));
pause(0.2);  % tiny pause so clear finishes cleanly
webread(baseUrl + "/control?cmd=start", weboptions("ContentType","json","Timeout",5));

% -------- Storage --------
nMax = ceil(duration/dt) + 10;
tVals  = nan(nMax,1);
lrVals = nan(nMax,1);
udVals = nan(nMax,1);

% -------- Plot setup --------
figure;
h1 = plot(nan, nan, 'LineWidth', 1.5);
hold on;
h2 = plot(nan, nan, 'LineWidth', 1.5);
hold off;
grid on;
xlabel('Time (s)');
ylabel('Angle (deg)');
title('Live phyphox Inclination');
legend('Left/Right', 'Vertical', 'Location', 'best');

% -------- Live loop --------
k = 0;
tStart = tic;

while toc(tStart) < duration
    try
        % Ask for the latest value from each buffer
        url = baseUrl + "/get?" + bufT + "=1&" + bufLR + "=1&" + bufUD + "=1";
        data = webread(url, weboptions("ContentType","json","Timeout",5));

        % Read newest sample
        tNow  = data.buffer.(bufT).buffer(end);
        lrNow = data.buffer.(bufLR).buffer(end);
        udNow = data.buffer.(bufUD).buffer(end);

        % Append only if time advanced
        if k == 0 || tNow > tVals(k)
            k = k + 1;
            tVals(k)  = tNow;
            lrVals(k) = lrNow;
            udVals(k) = udNow;

            set(h1, 'XData', tVals(1:k), 'YData', lrVals(1:k));
            set(h2, 'XData', tVals(1:k), 'YData', udVals(1:k));
            drawnow limitrate
        end

    catch ME
        warning("Read failed: %s", ME.message);
    end

    pause(dt);
end

% -------- Stop experiment --------
webread(baseUrl + "/control?cmd=stop", weboptions("ContentType","json","Timeout",5));

% -------- Final table --------
T = table(tVals(1:k), lrVals(1:k), udVals(1:k), ...
    'VariableNames', {'Time_s','LeftRight_deg','Vertical_deg'});

disp(T)
writetable(T, 'phyphox_live_tilt_data.csv');