import numpy as np
import os
import torch
from torch.utils.data.sampler import SubsetRandomSampler


class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, data_x, data_y):
        self.data_x = data_x
        self.data_y = data_y

    def __getitem__(self, index):
        image = self.data_x[index]
        label = self.data_y[index]

        return (image, label)


def get_train_val_loader(config, pin_memory, num_workers=1):
    level, batch_size = config.level, config.batch_size
    data_dir = '/hddraid5/data/colin/'

    if str(config.task).lower() == 'hela':
        mmap = False
        bits = int(np.log2(level))
        train_x_path = os.path.join(data_dir, 'ctc', 'train_x_norm.npy')
        train_y_path = os.path.join(data_dir, 'ctc', f'new_nuc_train_kb{bits}.npy')
        val_x_path = os.path.join(data_dir, 'ctc', 'val_x_norm.npy')
        val_y_path = os.path.join(data_dir, 'ctc', f'new_nuc_val_kb{bits}.npy')
        channels_first = False
    else:
        mmap = True
        train_x_path = os.path.join(data_dir, 'train_x1_norm.npy')
        train_y_path = os.path.join(data_dir, f'train_level_{level}_y1.npy')
        val_x_path = os.path.join(data_dir, 'val_x1_norm.npy')
        val_y_path = os.path.join(data_dir, f'val_level_{level}_y1.npy')
        channels_first = True

    # pytorch says channels fist
    if mmap:
        train_x = torch.from_numpy(np.load(train_x_path, mmap_mode='r'))
        train_y = torch.from_numpy(np.load(train_y_path, mmap_mode='r'))

        val_x = torch.from_numpy(np.load(val_x_path, mmap_mode='r'))
        val_y = torch.from_numpy(np.load(val_y_path, mmap_mode='r'))
    else:
        train_x = torch.from_numpy(np.load(train_x_path)).float()
        train_y = torch.from_numpy(np.load(train_y_path)).float()

        val_x = torch.from_numpy(np.load(val_x_path)).float()
        val_y = torch.from_numpy(np.load(val_y_path)).float()


    train_dataset = CustomDataset(train_x, train_y)
    val_dataset = CustomDataset(val_x, val_y)

    train_idx, valid_idx = list(range(train_x.shape[0])), list(range(val_x.shape[0]))

    train_sampler = SubsetRandomSampler(train_idx)
    valid_sampler = SubsetRandomSampler(valid_idx)
    train_loader = torch.utils.data.DataLoader(
        train_dataset, batch_size=batch_size, sampler=train_sampler,
        num_workers=num_workers, pin_memory=pin_memory,
    )

    valid_loader = torch.utils.data.DataLoader(
        val_dataset, batch_size=batch_size, sampler=valid_sampler,
        num_workers=num_workers, pin_memory=pin_memory,
    )

    return train_loader, valid_loader
