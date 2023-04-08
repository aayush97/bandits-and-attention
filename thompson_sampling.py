# Implement vanilla Thompson sampling
import random as rand
import heapq
import numpy as np

# Create Random bandit machine with unknown mean and variance
class Bandit:
    def __init__(self, id_no, estimation_threshold):
        '''
        true_mean: The true reward probability of receiving reward from this bandit
        '''
        self.true_mean = rand.random()
        self.id_no = id_no
        self.threshold = estimation_threshold
    
    def sample(self):
        '''
        Returns: Bernoulli reward with probability of the mean of the Bandit
        '''
        if rand.random() < self.true_mean:
            return 1
        
        else:
            return 0
    
    def show_mean(self):
        return ("The true mean for Bandit ", self.id_no, " is ", self.true_mean)
    
    def guess(self, guess):
        '''
        Guess: A float of the estimated mean for the bandit
        
        Returns:
            True if value is within threshold, False otherwise
        '''
        isTrue = abs(self.true_mean - guess)

        if isTrue <= self.threshold:
            return True
        
        return False

# This Agent plays the game and makes estimates on the 
class TSBernoulli_Agent:
    def __init__(self, epsilon, decay_rate, epsilon_end):
        self.bandit_interactions = {} #maybe make this a heap in the future
        self.epsilon = epsilon
        self.decay = decay_rate
        self.epsilon_end = epsilon_end
        self.action_count = 0

    def choose_bandit(self):
        '''
        Sample each known bandit by its variance distribution and select
        max estimate with probability epsilon
        '''
        
        highest_estimate_id = 0
        highest_estimate = None


        for bandit in self.bandit_interactions.keys():
            #Get the variance of the bandit
            bandit_alpha = self.bandit_interactions[bandit][0]
            bandit_beta = self.bandit_interactions[bandit][1]
            
            #Get a random number for the estimate variance
            x = np.random.beta(bandit_alpha, bandit_beta)
            
            #If it is the highest, save it
            if highest_estimate is None or x > highest_estimate:
                highest_estimate_id = bandit
                highest_estimate = x                                          

        self.action_count += 1
        if self.action_count % 10 == 0:
            self.epsilon = max(self.epsilon_end, self.epsilon * self.decay)

        # Explore   
        if rand.random() < self.epsilon:
            b = rand.randint(0, len(self.bandit_interactions)-1)           
            return b

        # Take the greedy choice
        else:
            return highest_estimate_id

    def update_estimates(self, reward, id):
        '''
        Reward: The reward received from a bandit
        ID: The id number of the bandit
        '''
        #Update reward count and visit count
        a, b, c, rc = self.bandit_interactions[id]

        if reward == 1:
            self.bandit_interactions[id] = (a + 1, b, c + 1, rc+reward) 
        
        else: # reward is 0
            self.bandit_interactions[id] = (a, b + 1, c + 1, rc) 
        
        return

    def add_bandit(self, id, bandit_alpha = 1, bandit_beta = 1 ):
        '''
        ID: ID number of the bandit to be added to self history
        Bandit_alpah/beta: The estimated reward from the bandit, initialized to 1 for uniform beta distribution
        '''
        # Bandit item has tuple (alpha, beta, visit_count, cumulative_reward)
        self.bandit_interactions[id] = (bandit_alpha, bandit_beta, 0, 0)
        
        return False
    
    def show_estimates(self):
        '''
        Return a list of each bandit and assumed win probability
        '''
        estimates = list()

        for key in self.bandit_interactions:

            estimates.append((key,self.bandit_interactions[key][0]/self.bandit_interactions[key][2]))
        
        return estimates

if __name__ == '__main__':
    threshold = 0.05
    epsilon = 0
    decay = 0.995
    epsilon_end = 0.0
    bandits_count = 10
    episodes = 5000

    bandits = {}
    agent = TSBernoulli_Agent(epsilon, decay, epsilon_end)

    for i in range(bandits_count):
        x = Bandit(i, threshold)
        print(x.show_mean())
        bandits[i] = x
        agent.add_bandit(i)

    for e in range(episodes):
        choice = agent.choose_bandit()
        #print("choice is ", choice)
        reward = bandits[choice].sample()
        agent.update_estimates(reward, choice)


    # Check our work
    count_correct=0
    est = agent.show_estimates()
    print(est)
    
    # Does not get approximation for every bandit
    # When it gets a correct approximation, it is because agent
    # noticed it gave a higher reward distribution and played it again

    for b, m in est:
        y = bandits[b].guess(m)
        print(y)
        if y:
            count_correct +=1
            print("Bandit ", b, " has reward distribution ", m)
    
    if count_correct >= 2:
        print("Found the top achievers")
    else:
        print("Not quite.")