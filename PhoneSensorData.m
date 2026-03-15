%% Live phyphox inclination acquisition -> append to CSV until key press
clear; clc;

% -------- User settings --------
baseUrl  = "http://172.20.10.1";   % replace with your phone's phyphox URL
dt       = 0.1;                    % polling interval in seconds
fileName = fullfile(pwd, 'PhoneSensorData.csv');

% Buffers you want
bufT  = "t";
bufLR = "tiltFlatLR";
bufUD = "tiltFlatUD";

% -------- Check connection --------
webread(baseUrl + "/config", weboptions("ContentType","json","Timeout",5));

% -------- Create/overwrite CSV and write header --------
fid = fopen(fileName, 'w');
fprintf(fid, 'Time_s,LeftRight_deg,Vertical_deg\n');
fclose(fid);

% -------- Reset and start experiment --------
webread(baseUrl + "/control?cmd=clear", weboptions("ContentType","json","Timeout",5));
pause(0.2);
webread(baseUrl + "/control?cmd=start", weboptions("ContentType","json","Timeout",5));

% -------- Control window --------
stopFig = figure( ...
    'Name', 'phyphox acquisition control', ...
    'NumberTitle', 'off', ...
    'MenuBar', 'none', ...
    'ToolBar', 'none', ...
    'Color', 'w', ...
    'KeyPressFcn', @(src,event) setappdata(src, 'stopNow', true));

setappdata(stopFig, 'stopNow', false);

uicontrol( ...
    'Style', 'text', ...
    'String', 'Press any key in this window to stop acquisition', ...
    'Units', 'normalized', ...
    'Position', [0.1 0.4 0.8 0.2], ...
    'BackgroundColor', 'w', ...
    'FontSize', 12);

lastT = -inf;

try
    while ishandle(stopFig) && ~getappdata(stopFig, 'stopNow')
        try
            url = baseUrl + "/get?" + bufT + "=1&" + bufLR + "=1&" + bufUD + "=1";
            data = webread(url, weboptions("ContentType","json","Timeout",5));

            tNow  = data.buffer.(bufT).buffer(end);
            lrNow = data.buffer.(bufLR).buffer(end);
            udNow = data.buffer.(bufUD).buffer(end);

            % Only append new samples
            if tNow > lastT
                fid = fopen(fileName, 'a');
                fprintf(fid, '%.6f,%.6f,%.6f\n', tNow, lrNow, udNow);
                fclose(fid);

                lastT = tNow;
            end
        catch
            % Skip failed reads
        end

        drawnow;
        pause(dt);
    end
catch
    % Falls through to cleanup below
end

% -------- Stop experiment --------
try
    webread(baseUrl + "/control?cmd=stop", weboptions("ContentType","json","Timeout",5));
catch
end

% -------- Close control window if still open --------
if exist('stopFig', 'var') && ishandle(stopFig)
    close(stopFig);
end