% this is the test for adjustment of demand charge 
% shape the peak of the worst day to the peak of the next worst day
% take the July 2018 net demand data from CAISO as an example

clc;clear;



%%  this is for illustration


% read the data in 
num_days = 1; 
NetDemand = zeros(96,num_days);  % every five-minutes data, each day we have 288 data points


for i = 1:num_days
    NetDemand = xlsread('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\example.xlsx','Sheet2','I3:I98');
end


P_limit = 24000; 
delta_t = 15;  % every 15 mins there is a data point
n_adjust_interval_lower= 6; 

[NetDemand_new, t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand, P_limit, delta_t,  n_adjust_interval_lower);


x = [1:96]'; 
plot(x, NetDemand);
hold on;
plot(x, NetDemand_new);


