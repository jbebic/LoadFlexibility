function [NetDemand_new, t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand, P_limit, delta_t,  n_adjust_interval_lower)

% This function is to adjust the net demand curve, so that the peak is <=
% P_limit
% NetDemand, NetDemand_new are column vectors
% P_limit is a positive number
% delta_t: time interval, e.g., there is a data point every 15 mins
   

n_data = length (NetDemand);   
Diff = P_limit * ones(n_data,1) - NetDemand; 
tol = 0.002; 


Intg_Diff = zeros(n_data,1);
Intg_Diff(1) = Diff(1) * delta_t; 
% % slope_Intg_Diff = zeros(n_data,1);  % positive or negative, -1: nagative; 1: positive
% % slope_Intg_Diff (n_data) = 1; 

for i = 2:n_data
    Intg_Diff(i)=  Intg_Diff(i-1) + Diff(i) * delta_t;
end

% % % % for i = 1:(n_data-1)
% % % %     if Intg_Diff(i+1) - Intg_Diff(i) >= 0
% % % %         slope_Intg_Diff(i) = 1;    % positive slope
% % % %     else
% % % %         slope_Intg_Diff(i) = -1;   % negative slope
% % % %     end
% % % %     
% % % % end
% % % % 
% % % % %% find from which time interval, the slope is changing
% % % % status = zeros(n_data,1); 
% % % % status(n_data) = 0;   
% % % % 
% % % % for i = 1:(n_data-1)
% % % %     if  slope_Intg_Diff(i+1) * slope_Intg_Diff(i) > 0 
% % % %         status(i) = 0;    % status no change
% % % %     else
% % % %         status(i) = 1; % status change
% % % %     end
% % % %     
% % % % end

A  = find(Diff<=0);   % this is the start and end of negative segment 

Target_Intg_Diff = (Intg_Diff(A(1))+ Intg_Diff(A(end)))/2; 

% find the most closest three 
[Intg_diff1 ,index1] = min(abs(Intg_Diff (1:(A(1)-1)) - Target_Intg_Diff)); 
[Intg_diff2 ,index2] = min(abs(Intg_Diff(A(1):A(end)) -  Target_Intg_Diff)); 
[Intg_diff3 ,index3] = min(abs(Intg_Diff((A(end)+1):end) -  Target_Intg_Diff)); 


Index = sort([index1; (index2+A(1)-1); (index3+A(end))]); 

t_start = Index(1) + 2;  % somtimes, +1 is better, this is to address the unbalance problem
t_end = Index(end);  

EnergyConspt = 0 ; 
EnergyConspt_new = 0 ; 

for i = t_start  : t_end 
    EnergyConspt = EnergyConspt + NetDemand(i)*delta_t;
    EnergyConspt_new = EnergyConspt_new + P_limit*delta_t;
    
end



    NetDemand_new  =  NetDemand; 
    NetDemand_new (t_start : t_end) = P_limit * ones((t_end-t_start+1),1);
    
    
    
    if  EnergyConspt ==  EnergyConspt_new
        
        return;
        
    else
        
    
     
        
        
        if  EnergyConspt - EnergyConspt_new > 0   % if not enough, adjust the prevoius n_adjust_interval_lower before t_start
            
            delta_adjust = (EnergyConspt - EnergyConspt_new)/ n_adjust_interval_lower/delta_t ;
            
            NetDemand_new ((t_start-n_adjust_interval_lower): (t_start-1)) = NetDemand((t_start-n_adjust_interval_lower): (t_start-1)) + delta_adjust;
            
            
        else
            delta_adjust = (-EnergyConspt + EnergyConspt_new)/ n_adjust_interval_lower/delta_t ;
            
            NetDemand_new ((t_start-n_adjust_interval_lower): (t_start-1)) = NetDemand((t_start-n_adjust_interval_lower): (t_start-1)) - delta_adjust;
            
            
            
% % % % %             % keep the middle interval in [t_start, t_end] not change, adjust other intervals
% % % % %             
% % % % %             if t_end - t_start ==4  % we can only asjust the previous n_adjust_interval_lower before t_start
% % % % %             
% % % % %       
% % % % %             delta_adjust = (-EnergyConspt + EnergyConspt_new)/ n_adjust_interval_lower/delta_t ;
% % % % %             
% % % % %             NetDemand_new ((t_start-n_adjust_interval_lower): (t_start-1)) = NetDemand((t_start-n_adjust_interval_lower): (t_start-1)) - delta_adjust;
% % % % %             
% % % % %             else
% % % % %                 
% % % % %                 n_adjust_interval = t_end - t_start-3 +1;   % three interval still remain P_limit
% % % % %                 delta_adjust = (-EnergyConspt + EnergyConspt_new)/ n_adjust_interval/delta_t ;
% % % % %                 t_middle = floor((t_end-t_start)/2)  + t_start; 
% % % % %                 NetDemand_new(t_start : ( t_middle-1)) =  P_limit- delta_adjust; 
% % % % %                 NetDemand_new((t_middle+3) : t_end) =  P_limit - delta_adjust; 
% % % % %                 
% % % % %                 
% % % % %             end
            
            
        end
        
        
        EnergyConspt_adjust =  sum(NetDemand((t_start-n_adjust_interval_lower)  : t_end)) *delta_t ;
        EnergyConspt_new_adjust =  sum(NetDemand_new((t_start-n_adjust_interval_lower)  : t_end)) *delta_t ;
        
        
        diff_adjust = EnergyConspt_adjust - EnergyConspt_new_adjust;
        
        
        
        
end





