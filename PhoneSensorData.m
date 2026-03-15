%% Live phyphox inclination acquisition -> save CSV only
clear; clc;

% -------- User settings --------
baseUrl  = "http://172.20.10.1";   % replace with your phone's phyphox URL
duration = 5;                      % seconds to run
dt       = 0.1;                    % polling interval in seconds

% Buffers you want
bufT  = "t";
bufLR = "tiltFlatLR";    % left/right
bufUD = "tiltFlatUD";    % vertical (up/down)

% -------- Make sure remote interface is reachable --------
webread(baseUrl + "/config", weboptions("ContentType","json","Timeout",5));

% -------- Reset and start experiment --------
webread(baseUrl + "/control?cmd=clear", weboptions("ContentType","json","Timeout",5));
pause(0.2);
webread(baseUrl + "/control?cmd=start", weboptions("ContentType","json","Timeout",5));

% -------- Storage --------
nMax = ceil(duration/dt) + 10;
tVals  = nan(nMax,1);
lrVals = nan(nMax,1);
udVals = nan(nMax,1);

% -------- Live acquisition loop --------
k = 0;
tStart = tic;

while toc(tStart) < duration
    try
        url = baseUrl + "/get?" + bufT + "=1&" + bufLR + "=1&" + bufUD + "=1";
        data = webread(url, weboptions("ContentType","json","Timeout",5));

        tNow  = data.buffer.(bufT).buffer(end);
        lrNow = data.buffer.(bufLR).buffer(end);
        udNow = data.buffer.(bufUD).buffer(end);

        if k == 0 || tNow > tVals(k)
            k = k + 1;
            tVals(k)  = tNow;
            lrVals(k) = lrNow;
            udVals(k) = udNow;
        end

    catch
        % skip failed reads
    end

    pause(dt);
end

% -------- Stop experiment --------
webread(baseUrl + "/control?cmd=stop", weboptions("ContentType","json","Timeout",5));

% -------- Final table --------
T = table(tVals(1:k), lrVals(1:k), udVals(1:k), ...
    'VariableNames', {'Time_s','LeftRight_deg','Vertical_deg'});

% -------- Save CSV to current folder --------
writetable(T, fullfile(pwd, 'PhoneSensorData.csv'));