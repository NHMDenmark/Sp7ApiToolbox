SELECT DISTINCT(t1.TaxonID), t1.RankID, t1.FullName, t1.Author, t1.ParentID, p1.Name ParentName  
               ,t2.TaxonID,  t2.RankID, t2.FullName, t2.Author, t2.ParentID, p2.Name ParentName 
FROM taxon t1 
	LEFT JOIN taxon t2 ON t1.FullName = t2.FullName AND t1.TaxonID <> t2.TaxonID 
	LEFT JOIN taxon p1 ON p1.TaxonID = t1.ParentID
	LEFT JOIN taxon p2 ON p2.TaxonID = t2.ParentID
	WHERE t1.TaxonTreeDefID = 13 
	  AND t2.TaxonTreeDefID = 13
	  AND t1.RankID > 180 AND t2.RankID > 180 -- Restrict to below genus 
	  -- AND (t1.Author IS NULL OR t2.Author IS NULL)
	ORDER BY t1.FullName -- TaxonID 
/*
	  UNION 
	  
SELECT DISTINCT(t2.TaxonID), t2.RankID, t2.FullName, t2.Author, t2.ParentID, p2.Name ParentName
FROM taxon t1 
	LEFT JOIN taxon t2 ON t1.FullName = t2.FullName AND t1.TaxonID <> t2.TaxonID 
	LEFT JOIN taxon p1 ON p1.TaxonID = t1.ParentID
	LEFT JOIN taxon p2 ON p2.TaxonID = t2.ParentID
	WHERE t1.TaxonTreeDefID = 13 
	  AND t2.TaxonTreeDefID = 13
	  AND t1.RankID > 180 AND t2.RankID > 180 -- Restrict to below genus   
	  -- AND (t1.Author IS NULL OR t2.Author IS NULL)

ORDER BY TaxonId
*/
;