function [NetDemand_new, t_start, t_end,EnergyConspt, EnergyConspt_new, diff_adjust] = NetDemandAdjust (NetDemand, P_limit, delta_t,  n_adjust_interval_lower)

% This function is to adjust the net demand curve, so that the peak is <=
% P_limit
% NetDemand, NetDemand_new are column vectors
% P_limit is a positive number
% delta_t: time interval, e.g., there is a data point every 15 mins

n_data = length (NetDemand);
Diff = P_limit * ones(n_data,1) - NetDemand;

Intg_Diff = zeros(n_data,1);
Intg_Diff(1) = Diff(1) * delta_t;


for i = 2:n_data
    Intg_Diff(i)=  Intg_Diff(i-1) + Diff(i) * delta_t;
end

A  = find(Diff<=0);   % this is to find the start and end of negative segment
Target_Intg_Diff = (Intg_Diff(A(1))+ Intg_Diff(A(end)))/2;

% find the most closest three
[~ ,index1] = min(abs(Intg_Diff (1:(A(1)-1)) - Target_Intg_Diff));
[~ ,index2] = min(abs(Intg_Diff(A(1):A(end)) -  Target_Intg_Diff));
[~ ,index3] = min(abs(Intg_Diff((A(end)+1):end) -  Target_Intg_Diff));


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
    end
    EnergyConspt_adjust =  sum(NetDemand((t_start-n_adjust_interval_lower)  : t_end)) *delta_t ;
    EnergyConspt_new_adjust =  sum(NetDemand_new((t_start-n_adjust_interval_lower)  : t_end)) *delta_t ;
    
    diff_adjust = EnergyConspt_adjust - EnergyConspt_new_adjust;
    
end





