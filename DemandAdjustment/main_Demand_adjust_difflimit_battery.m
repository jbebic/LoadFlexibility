% this is the test for adjustment of demand charge 
% shape the peak of the worst day to the peak of the next worst day
% take the July 2018 net demand data from CAISO as an example

clc;clear;


% read the data in 
num_days = 31; 
index_days = xlsread('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\data.xlsx','Index_battery','A1:A31');
delta_t = 15;  % every 15 mins there is a data point
n_adjust_interval_lower= 4; 
num_datapoint = 96; 

NetDemand_ab = zeros(num_datapoint,num_days); % generate NetDemand absolute value
NetDemand  = zeros(num_datapoint,num_days); % generate NetDemand per unit value

for i = 1: num_days 
    
    NetDemand2 = csvread(strcat('C:\Users\212733910\Box Sync\Xian Guo\Projects\2018\NODES\dmand charge adjustment\study\data\July 2018\CAISO-netdemand-',...
        strcat(num2str(index_days(i)),'.csv')),3,1);  % data points every five mins
    
    for j = 1:96
        
        NetDemand_ab(j,i) = NetDemand2(3*(j-1)+1);
    end
    
end

NetDemand_average = sum(sum(NetDemand_ab,2))/ (num_days*num_datapoint);   % monthly average netdemand for the 15 min data points
NetDemand =  NetDemand_ab./NetDemand_average; 


Max_eachday = max(NetDemand,[],1);    % find the peak load for each day

Max_eachday_ordered = sort(Max_eachday); % from the smallest to largest daily peak

[~,index_peak_day] = max(Max_eachday); % find which day has the highest peak and define the demand charge

% B = sort(findpeaks(NetDemand(:,index_peak_day)));

SecondPeak_peakday =  0.9017;  %%%%% not sure how to find it, currently just eyeball it. 


num_Iteration = 9;  % how many iterations would like to adjust

NetDemand_new = zeros(num_datapoint,num_Iteration); 
Battery_bh = zeros(num_datapoint,num_Iteration);   % charging/ discharging behavior of battery
Battery_SOC = zeros(num_datapoint,num_Iteration);  % state of charge of battery
Battery_SOC_initial = 0.3; 

x = [1:num_datapoint]';


if  Max_eachday_ordered(num_days-1) <= SecondPeak_peakday
    disp('it hits the second peak on iteration');
    disp(1);
    
else
    [NetDemand_new(:,1), t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand(:,index_peak_day), Max_eachday_ordered(num_days-1), delta_t, n_adjust_interval_lower);
    Battery_bh(:,1) = NetDemand_new(:,1) - NetDemand(:,index_peak_day);
    Battery_SOC(1,1) =  Battery_SOC_initial + Battery_bh(1,1) ;
    for m = 2 :  num_datapoint
        Battery_SOC(m,1) = Battery_SOC(m-1,1) + Battery_bh(m,1);
    end
    
    figure(1);
    subplot(3,1,1);
    
    plot(x, NetDemand(:,index_peak_day),'b',x, NetDemand_new(:,1), 'r--', 'LineWidth',1);
    % xlim([60 96]);
    %  ylim([0.8,1.6]);
    
    title(strcat('Plimit=',num2str(Max_eachday_ordered(num_days-1))));
    
    
    subplot(3,1,2);
    plot(x, Battery_bh(:,1));
    title('battery hehavior');
    
    subplot(3,1,3);
    plot(x, Battery_SOC(:,1));
    title('battery state of charge');
    
end
 

 for k = 2:  num_Iteration
     
     if  Max_eachday_ordered(num_days-1) <= SecondPeak_peakday
         disp('it hits the second peak on iteration');
         disp(k);
         
     else
         [NetDemand_new(:,k), t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand_new(:,k-1), Max_eachday_ordered(num_days-k), delta_t, n_adjust_interval_lower);
         Battery_bh(:,k) = NetDemand_new(:,k) - NetDemand(:,index_peak_day);
         
         Battery_SOC(1,k) =  Battery_SOC_initial + Battery_bh(1,k) ;
         for m = 2 :  num_datapoint
             Battery_SOC(m,k) = Battery_SOC(m-1,k) + Battery_bh(m,k);
         end
     
         figure(k);
       %  title(strcat(num2str(k),'th adjustment'))
         subplot(3,1,1);
         plot(x, NetDemand(:,index_peak_day),'b',x, NetDemand_new(:,k), 'r--', 'LineWidth',1);
         title(strcat('Plimit=',num2str(Max_eachday_ordered(num_days-k))));
         
         
         subplot(3,1,2);
         plot(x, Battery_bh(:,k));
         title('battery behavior');
         
         subplot(3,1,3);
         plot(x, Battery_SOC(:,k));
         title('battery state of charge');
         
     end
     
 end

    
    
    
    
    
    
    
    
    
    
    
    
    




