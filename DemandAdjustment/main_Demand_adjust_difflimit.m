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


P_limit = [ 28500; 28000;27500;  27000; 26500; 26000; 25500]; 
delta_t = 15;  % every 15 mins there is a data point
n_adjust_interval_lower= 4; 

x = [1:96]'; 
plot(x, NetDemand);
hold on;


NetDemand_new = zeros(length(NetDemand),length(P_limit));

[NetDemand_new(:,1), t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand, P_limit(1), delta_t,  n_adjust_interval_lower);


plot(x, NetDemand_new(:,1),'--','LineWidth',0.75);
hold on; 


for i = 2:length(P_limit)

[NetDemand_new(:,i), t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand_new(:,i-1), P_limit(i), delta_t,  n_adjust_interval_lower);


plot(x, NetDemand_new(:,i),'--','LineWidth',0.75);
hold on; 

end

legend('Original','Plimit = 28500','Plimit = 28000','Plimit = 27500','Plimit = 27000','Plimit = 26500','Plimit = 26000','Plimit = 25500','Location','northwest');
