# LoadFlexibility
The repository contains a tool-chain for evaluating flexibility of electric loads using interval meter data.

Because the data files are relatively large, the tools are built assuming file inputs and outputs, to enable running portions of the tool-chain without the need to re-run the analysis preceding the current step. For documentation on tool-chain components and file formats see documentation in the /doc folder.

# Overview
Most processes using electric power have flexibility in terms of temporal usage of energy. Given a state of process technology, generating an output from a process requires a known amount of energy, but in most cases, it is not essential that this energy be supplied at a steady pace. If water is being pumped for irrigation it is necessary to deliver a defined volume of water, but it is not essential to deliver this volume at a constant speed over time.

The technology to enable flexibility is readily available. Expanding on the example of irrigation, the enabling technology is a variable speed drive for the pump motor. While variable speed drives are a commodity today, they are still more expensive than an on/off contactor, so the question to answer is not: <em>Can this be done?</em>, but rather: <em>Do the benefits of using load flexibility outweigh the cost of its enablement?</em> In other words, does paying extra for the variable speed drive and subjecting it to aggregation control for orchestration of flexibility create enough benefits someplace else to make the investment worthwhile.

The benefits of using load flexibility are primarily associated with reducing power system operating costs. This has two main components:

1.	Reducing the amount of spinning reserves needed to deal with the combined uncertainty of load and variable renewable generation, and
1.	Modifying the shape of net load to maximize utilization of renewable energy and thus reduce curtailments.   

The tools in this repository use utility interval meter data to quantify load flexibility in the context of the second item. We study the patterns of consumption of similar loads relative to the time-of-use (TOU) utility rates and quantify the differences in energy consumed at the time of high prices. The combination of [NAICS](https://www.census.gov/eos/www/naics/) code and a time-of-use rate is used as a measure of similarity. For example, grocery stores (NAICS code 4451*) subscribed to a [TOU-GS-3 rate](https://www.sce.com/NR/sc3/tm2/pdf/CE281.pdf) is a pairing that determines similarity.

For each group, the loads are ranked based on what they pay for energy: the ones that pay the least are called <em>leaders</em> and all the rest are called <em>others</em>. The difference between the normalized consumption of <em>leaders</em> and <em>others</em> yields daily duration curves of flexibility. The process yields a normalized duration curve of flexibility for every day of the year. The curves are separated for seasons of the year and, within each season, into weekdays and weekends (including public holidays).

This is used as input to production simulation tools to modify the daily load profiles and measure the avoided cost by exercising load flexibility.  

The production simulation tool then modifies the original load profiles to maximize the system benefit, while ensuring that the delta between modified and original load profiles has the duration curve that does not exceed the flexibility duration curve supplied by this analysis.

# Disclaimer
This is a high-level overview. Additional details are provided in the comments of various code modules and in the documentation.
