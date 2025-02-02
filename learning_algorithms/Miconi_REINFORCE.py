import numpy as np

from learning_algorithms.Learning_Algorithm import Learning_Algorithm


class Miconi_REINFORCE(Learning_Algorithm):
    def __init__(self, rnn, sigma=0, p=1, n_trial_types=1, **kwargs):
        """Inits an instance of REINFORCE by specifying the optimizer used to
        train the A and alpha values and a noise standard deviation for the
        perturbations.
        Args:
            optimizer (optimizers.Optimizer): An instance of the Optimizer class
            sigma_noise (float): Standard deviation for the values, sampled
                i.i.d. from a zero-mean Gaussian, used to perturb the network
                state to noisy_rnn and thus estimate target predictions for
                A and alpha.
            p (float): Probability for perturbing a given node
        Keyword args:
            decay (numpy float): value of decay for the eligibility trace.
                Must be a value between 0 and 1, default is 0, indicating
                no decay.
            loss_decay (numpy float): time constant of the filtered average of
                the activations."""

        self.name = 'Miconi_REINFORCE'
        allowed_kwargs_ = {'decay', 'loss_decay', 'h_avg_decay',
                           'tau_e_trace', 'reset_h_avg'}
        super().__init__(rnn, allowed_kwargs_, **kwargs)
        # Initialize learning variables
        if self.decay is None:
            self.decay = 1
        if self.loss_decay is None:
            self.loss_decay = 0.01
        if self.h_avg_decay is None:
            self.h_avg_decay = 0.03
        if self.reset_h_avg is None:
            self.reset_h_avg = True
        self.h_avg = np.zeros(self.n_h)
        self.tau_e_trace = 0.05
        self.e_trace = 0
        self.loss_avg = [0] * n_trial_types
        self.loss_prev = 0
        self.loss = 0
        self.sigma = sigma
        self.p = p

    def update_learning_vars(self):
        """Updates the eligibility traces used for learning"""
        # presynaptic variables/parameters

        ### random perturbations from here?

        self.a_hat = np.concatenate([self.rnn.a_prev,
                                     self.rnn.x,
                                     np.array([1])])

        self.h_avg = (1 - self.h_avg_decay) * self.h_avg + self.h_avg_decay * self.rnn.h

        # postsynaptic variables/parameters
        self.D = self.rnn.h - self.h_avg

        # matrix of pre/post activations
        self.e_immediate = np.outer(self.D, self.a_hat)
        # self.e_trace = ((1 - self.tau_e_trace) * self.e_trace\
        #                + self.tau_e_trace * self.e_immediate**3)
        self.e_trace = self.e_trace + self.e_immediate ** 3
        self.loss_prev = self.loss
        self.loss = self.rnn.loss_
        i_tt = self.rnn.trial_type
        self.loss_avg[i_tt] = ((1 - self.loss_decay) * self.loss_avg[i_tt] +
                               self.loss_decay * self.loss_prev)

        ### --- Perturb system for next time step --- ###
        self.pert = np.random.binomial(1, p=self.p, size=self.n_h)
        self.pert = self.pert * np.random.normal(0, self.sigma, self.n_h)

        self.rnn.h += self.pert

    def get_rec_grads(self):
        """Combine the eligibility trace and the reward to get an estimate
        of the gradient"""
        i_tt = self.rnn.trial_type
        return (self.loss - self.loss_avg[i_tt]) * self.e_trace

    def reset_learning(self):
        """Reset the eligibility traces to 0."""

        self.e_trace *= 0
        if self.reset_h_avg:
            self.h_avg *= 0
