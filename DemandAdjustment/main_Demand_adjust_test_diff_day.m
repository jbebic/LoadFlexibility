% this is the test for adjustment of demand charge 
% shape the peak of the worst day to the peak of the next worst day
% take the July 2018 net demand data from CAISO as an example

clc;clear;



%%  this is for illustration


% read the data in 
num_days = 20; 
index_days = xlsread('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\data.xlsx','Index','A1:A20');
[~,day_identifier] = xlsread('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\data.xlsx','Index','B1:B20');
delta_t = 15;  % every 15 mins there is a data point
n_adjust_interval_lower= 4; 

NetDemand = zeros(96,1); 


for i = 1: num_days 
    
    NetDemand2 = csvread(strcat('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\data\Typical_Day\CAISO-netdemand-',...
        strcat(num2str(index_days(i)),'.csv')),3,1);  % data points every five mins
    
    for j = 1:96
        
        NetDemand(j) = NetDemand2(3*(j-1)+1);
    end
    
    
       max_demand = max(NetDemand); 
       
       P_limit = floor(0.95*max_demand/1000)*1000;    % find the closest floor number xx,k to max_demand - 2k. 
    
       [NetDemand_new, t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand, P_limit, delta_t, n_adjust_interval_lower);
       
       x = [1:96]';
       figure(i)
       plot(x, NetDemand,'b',x, NetDemand_new, 'r--', 'LineWidth',1);
      % xlim([55,100]); % with this, more closer look  
      % ylim([12000, max_demand + 1000 ]);  % with this, more closer look
       title(strcat(num2str(index_days(i)),strcat('--',day_identifier{i})));
      % legend('NetDemand','NetDemand after adjustment','Location','southeast');    % this is for closer look
       legend('NetDemand','NetDemand after adjustment','Location','northwest');
        print(figure(i), '-dpdf',strcat('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\test results_diff day\', strcat(num2str(index_days(i)),'.pdf'))); % save to single pdf file, then merge them to a single pdf file
        display('finish');
        display(index_days(i));
       
end








