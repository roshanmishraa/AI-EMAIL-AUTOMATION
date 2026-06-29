import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getKBDocs, uploadKBDoc, deleteKBDoc } from '../api/kbApi';
export const useKBDocs = () => useQuery({
    queryKey: ['kb-docs'],
    queryFn: getKBDocs,
    select: res => res.data,
});
export const useUploadKBDoc = () => {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (form) => uploadKBDoc(form),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['kb-docs'] }),
    });
};
export const useDeleteKBDoc = () => {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: (id) => deleteKBDoc(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ['kb-docs'] }),
    });
};
